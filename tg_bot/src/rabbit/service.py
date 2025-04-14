import logging
from contextlib import asynccontextmanager

import aio_pika


logger = logging.getLogger(__name__)


class RabbitMQService:
    def __init__(self, rabbit_url: str, queue: str):
        self.rabbit_url = rabbit_url
        self.queue = queue
        self.connection = None
        self.channel = None

    @asynccontextmanager
    async def connect(self):
        try:
            logger.critical(f"Connecting to RabbitMQ server {self.rabbit_url}")
            self.connection = await aio_pika.connect_robust(self.rabbit_url)
            self.channel = await self.connection.channel()
            yield self
        finally:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()

    async def send_message(self, message):
        await self.channel.declare_queue(self.queue, durable=True)
        await self.channel.default_exchange.publish(
            routing_key=self.queue,
            message=aio_pika.Message(body=message.encode()),
        )
        logger.info(f"Sent message to {self.queue}")
