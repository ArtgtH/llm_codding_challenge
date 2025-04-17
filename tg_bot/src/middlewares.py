from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from rabbit.service import RabbitMQService


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
        data["publisher"] = self.rabbit_service
        return await handler(event, data)
