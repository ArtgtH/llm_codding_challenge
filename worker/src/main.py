import json
import logging
from datetime import datetime
from typing import Dict

import pika

from configs.config import settings
from db.base import session_factory
from db.repositories import DailyReportRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def some_magic(message: Dict[str, str | int]) -> bytes:
    print(message["chat_id"])
    print(message["chat_title"])
    print(message["user"])
    print(message["message"])
    print(message["time"])

    return b"Hello World"


def _callback(ch, method, properties, body):
    message = body.decode()
    message = json.loads(message)

    logger.info(message)

    report = some_magic(message)

    with session_factory() as db:
        DailyReportRepository(db).create_daily_report(
            chat_id=message.get("chat_id"),
            date=datetime.today().date(),
            report=report,
        )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    with pika.BlockingConnection(
        pika.URLParameters(settings.RABBITMQ_URL)
    ) as connection:
        with connection.channel() as channel:
            channel.queue_declare(queue=settings.RABBITMQ_MESSAGE_QUEUE, durable=True)

            channel.basic_consume(
                queue=settings.RABBITMQ_MESSAGE_QUEUE,
                on_message_callback=_callback,
            )
            channel.start_consuming()


if __name__ == "__main__":
    main()
