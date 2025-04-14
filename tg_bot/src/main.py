import asyncio
import logging
from typing import Callable, Any, Dict, Awaitable

from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.types import Message

from configs.config import settings
from db.base import async_session_factory, init_db
from db.repositories import MessageRepository
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
            data["repo"] = MessageRepository(session)
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


@dp.message()
async def handle_message(
    message: types.Message,
    repo: MessageRepository,
    publisher: RabbitMQService,
) -> None:
    try:
        await repo.create_message(
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

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
