import asyncio
import logging
from datetime import timedelta

from aiogram import Bot, Dispatcher, types

from configs.config import settings
from db.base import async_session_factory, init_db
from db.repositories import MessageRepository
from middlewares import RabbitMQMiddleware
from rabbit.service import RabbitMQService
from timer import ChatTimers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
logger = logging.getLogger(__name__)
timer = ChatTimers(bot)


@dp.message()
async def handle_message(
    message: types.Message,
    publisher: RabbitMQService,
) -> None:
    try:
        async with async_session_factory() as db:
            await MessageRepository(db).create_message(
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
            (message.date + timedelta(hours=3)).strftime("%d/%m/%Y, %H:%M:%S"),
        )

        await timer.reset_timer(message.chat.id)

    except Exception as e:
        logger.error("Failed to process message", exc_info=e)


async def shutdown():
    for task in timer.timers.values():
        task.cancel()


async def main():
    rabbit_service = RabbitMQService(
        settings.RABBITMQ_URL, settings.RABBITMQ_MESSAGE_QUEUE
    )
    dp.message.middleware(RabbitMQMiddleware(rabbit_service))

    await init_db()

    try:
        await dp.start_polling(bot, handle_as_tasks=True, close_bot_session=True)
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
