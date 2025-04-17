import json
import logging
from datetime import datetime, date
from typing import Dict

import pika

from configs.config import settings
from db.base import session_factory
from db.repositories import DailyReportRepository
from ai_agent.text_processing_pipeline import process_text_message, DEFAULT_EXCEL_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def some_magic(message: Dict[str, str | int]) -> bytes | None:
    """ 
    Processes the message text using the AI agent, updates an Excel log, 
    and returns the updated Excel file as bytes.
    """ 
    logger.info(f"Received message for processing: chat_id={message.get('chat_id')}, user={message.get('user')}")
    input_text = message.get("message", "") # Safely get message text
    input_date = message.get("time", None) # Safely get message textct
    input_date  = datetime.strptime(input_date, "%d/%m/%Y, %H:%M:%S")
    input_date = input_date.date()
    
    if not isinstance(input_text, str) or not input_text.strip():
        logger.warning("Received message with empty or invalid text content.")
        return b""
        

    excel_log_path = DEFAULT_EXCEL_PATH
    excel_bytes = process_text_message(text=input_text,  message_date=input_date,  excel_path=excel_log_path,)
    
    if excel_bytes:
        logger.info(f"Successfully processed message and generated Excel ({len(excel_bytes)} bytes).")
        return excel_bytes
    else:
        logger.error(f"Text processing failed or produced no data for message text: '{input_text[:100]}...'")
        return b""


def _callback(ch, method, properties, body):
    message = body.decode()
    message = json.loads(message)

    logger.info(message)

    if report := some_magic(message):
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
