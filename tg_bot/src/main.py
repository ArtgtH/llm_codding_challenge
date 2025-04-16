import asyncio
import logging
from datetime import datetime
from typing import Callable, Any, Dict, Awaitable

import pytz
from aiogram import Bot, Dispatcher, types, BaseMiddleware, exceptions
from aiogram.types import Message, BufferedInputFile

from configs.config import settings
from db.base import async_session_factory, init_db
from db.repositories import MessageRepository, DailyReportRepository
from rabbit.service import RabbitMQService

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[logging.StreamHandler()],
)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

logger = logging.getLogger(__name__)

LAST_MESSAGE_TIMER: Dict[int, datetime] = {}
ACTIVE_TASKS: Dict[int, asyncio.Task] = {}


class DatabaseMiddleware(BaseMiddleware):
	async def __call__(
			self,
			handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
			event: Message,
			data: Dict[str, Any],
	) -> Any:
		async with async_session_factory() as session:
			data["message_repo"] = MessageRepository(session)
			data["report_repo"] = DailyReportRepository(session)
			return await handler(event, data)


class RabbitMQMiddleware(BaseMiddleware):
	def __init__(self, rabbit_service: RabbitMQService):
		self.rabbit_service = rabbit_service
		super().__init__()

	async def __call__(
			self,
			handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
			event: Message,
			data: Dict[str, Any],
	) -> Any:
		async with self.rabbit_service.connect():
			data["publisher"] = self.rabbit_service
			return await handler(event, data)


class ChatTimers:
	def __init__(self):
		self.timers: Dict[int, asyncio.Task] = {}
		self.lock = asyncio.Lock()

	async def reset_timer(self, chat_id: int, repo: DailyReportRepository):
		async with self.lock:
			if task := self.timers.get(chat_id):
				task.cancel()
				try:
					await task
				except asyncio.CancelledError:
					pass

			new_task = asyncio.create_task(self._timer_task(chat_id, repo))
			self.timers[chat_id] = new_task

	async def _timer_task(self, chat_id: int, repo: DailyReportRepository):
		try:
			logger.info("Started timer")
			await asyncio.sleep(10)
			logger.info("Finished timer")

			report = await repo.get_daily_report(str(chat_id), datetime.today().date())
			logger.info(f"что-то вытащили {report}")

			msk_timezone = pytz.timezone("Europe/Moscow")
			report_datetime = datetime.now(msk_timezone)
			hour = report_datetime.hour
			day = report_datetime.day
			month = report_datetime.month
			year = report_datetime.year
			filename = f"{hour}_{day}_{month}_{year}_SlovarikDB.xlsx"

			input_file = BufferedInputFile(report, filename=filename)

			await bot.send_document(chat_id, document=input_file)

		except (exceptions.TelegramAPIError, exceptions.TelegramRetryAfter) as e:
			logger.warning(f"Telegram API error: {e}")
		except Exception as e:
			logger.error(f"Timer error: {e}")
		finally:
			async with self.lock:
				self.timers.pop(chat_id, None)


chat_timers = ChatTimers()


@dp.message()
async def handle_message(
		message: types.Message,
		message_repo: MessageRepository,
		report_repo: DailyReportRepository,
		publisher: RabbitMQService,
) -> None:
	try:
		chat_id = message.chat.id
		LAST_MESSAGE_TIMER[chat_id] = datetime.now()

		if existing_task := ACTIVE_TASKS.get(chat_id):
			existing_task.cancel()
			try:
				await existing_task
			except asyncio.CancelledError:
				pass

		await message_repo.create_message(
			message.chat.id,
			message.chat.title,
			message.from_user.id,
			message.from_user.full_name,
			message.text or "",
		)

		await publisher.send_message(
			str(message.chat.id),
			message.chat.title,
			message.from_user.full_name,
			message.text,
			message.date,
		)

		await chat_timers.reset_timer(message.chat.id, report_repo)

	except Exception as e:
		logger.error("Failed to process message", exc_info=e)


async def shutdown():
	for task in ACTIVE_TASKS.values():
		task.cancel()
	await asyncio.gather(*ACTIVE_TASKS.values(), return_exceptions=True)


async def main():
	rabbit_service = RabbitMQService(
		settings.RABBITMQ_URL, settings.RABBITMQ_MESSAGE_QUEUE
	)
	dp.message.middleware(RabbitMQMiddleware(rabbit_service))

	await init_db()
	dp.message.middleware(DatabaseMiddleware())

	try:
		await dp.start_polling(bot, handle_as_tasks=True, close_bot_session=True)
	finally:
		await shutdown()


if __name__ == "__main__":
	asyncio.run(main())
