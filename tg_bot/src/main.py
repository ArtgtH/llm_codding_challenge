import asyncio
import logging
import time
from typing import Callable, Any, Dict, Awaitable

from aiogram import Bot, Dispatcher, types, BaseMiddleware, exceptions
from aiogram.types import Message

from configs.config import settings
from db.base import async_session_factory, init_db
from db.repositories import MessageRepository, DailyReportRepository
from rabbit.service import RabbitMQService

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

logger = logging.getLogger(__name__)


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


class ChatTimerManager:
	def __init__(self, bot: Bot, report_repo: DailyReportRepository):
		self.bot = bot
		self.last_activity: Dict[int, float] = {}
		self.timers: Dict[int, asyncio.Task] = {}

	async def _schedule_notification(self, chat_id: int):
		try:
			await asyncio.sleep(120)
			last_time = self.last_activity.get(chat_id)

			if last_time and (time.time() - last_time) >= 120:
				try:
					await self.bot.send_message(
						chat_id,
						"Прошло 2 минуты с момента последнего сообщения!",
					)
				except exceptions.TelegramAPIError as e:
					logger.error(f"Ошибка Telegram: {e}")
				finally:
					self._cleanup(chat_id)

		except asyncio.CancelledError:
			logger.debug(f"Таймер для чата {chat_id} отменен")
		except Exception as e:
			logger.error(f"Ошибка в таймере: {e}", exc_info=True)
			self._cleanup(chat_id)

	def _cleanup(self, chat_id: int):
		self.last_activity.pop(chat_id, None)
		self.timers.pop(chat_id, None)

	def update_timer(self, chat_id: int):
		now = time.time()
		self.last_activity[chat_id] = now

		if existing_timer := self.timers.get(chat_id):
			if not existing_timer.done():
				existing_timer.cancel()

		self.timers[chat_id] = asyncio.create_task(
			self._schedule_notification(chat_id),
			name=f"chat_timer_{chat_id}",
		)


class TimerMiddleware(BaseMiddleware):
	def __init__(self, timer_manager: ChatTimerManager):
		self.timer_manager = timer_manager
		super().__init__()

	async def __call__(
			self,
			handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
			event: Message,
			data: Dict[str, Any],
	) -> Any:
		data["timer_manager"] = self.timer_manager
		return await handler(event, data)


@dp.message()
async def handle_message(
	message: types.Message,
	message_repo: MessageRepository,
	report_repo: DailyReportRepository,
	publisher: RabbitMQService,
) -> None:
	try:
		await message_repo.create_message(
			message.chat.id,
			message.chat.title,
			message.from_user.id,
			message.from_user.full_name,
			message.text or "",
		)

		await publisher.send_message(message.text)
	except Exception as e:
		logger.error("Failed to create message", exc_info=e)


async def main():
	rabbit_service = RabbitMQService(
		settings.RABBITMQ_URL, settings.RABBITMQ_MESSAGE_QUEUE
	)
	dp.message.middleware(RabbitMQMiddleware(rabbit_service))

	await init_db()
	dp.message.middleware(DatabaseMiddleware())

	timer_manager = ChatTimerManager(bot, DailyReportRepository())
	dp.message.middleware(TimerMiddleware(timer_manager))

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
