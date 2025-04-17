import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

logger = logging.getLogger(__name__)


class RabbitMQService:
    def __init__(self, rabbit_url: str, queue: str):
        self.rabbit_url = rabbit_url
        self.queue = queue
        self.connection_pool = Pool(self._create_connection, max_size=100)

    async def _create_connection(self) -> AbstractRobustConnection:
        connection = await connect_robust(self.rabbit_url)
        async with connection.channel() as channel:
            await channel.declare_queue(self.queue, durable=True)
        return connection

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[None, None]:
        async with self.connection_pool.acquire() as connection:
            async with connection.channel() as channel:
                yield channel

    async def send_message(
        self, chat_id: str, chat_title: str, user: str, text: str, time: str
    ):
        message = {
            "chat_id": chat_id,
            "chat_title": chat_title,
            "user": user,
            "message_text": text,
            "time": time,
        }
        json_message = json.dumps(message)

        async with self.connect() as channel:
            await channel.default_exchange.publish(
                Message(body=json_message.encode()),
                routing_key=self.queue,
            )
            logger.info(f"Send msg `{text[:20]}`")
