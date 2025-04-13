import asyncio
import logging
from typing import Callable, Any, Dict, Awaitable

from aiogram import Bot, Dispatcher, types, BaseMiddleware

from configs.config import settings
from db.base import async_session_factory, init_db
from db.repositories import MessageRepository


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            data["repo"] = MessageRepository(session)
            return await handler(event, data)


dp.message.middleware(DatabaseMiddleware())


@dp.message()
async def handle_message(
    message: types.Message,
    repo: MessageRepository,
) -> None:
    try:
        await repo.create_message(
            message.chat.id,
            message.chat.title,
            message.from_user.id,
            message.from_user.full_name,
            message.text or "",
        )
    except Exception as e:
        logger.error("Failed to create message", exc_info=e)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
