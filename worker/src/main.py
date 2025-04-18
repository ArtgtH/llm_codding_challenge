import json
import logging
from dataclasses import dataclass
from datetime import datetime

import pika

from configs.config import settings
from db.base import session_factory
from db.repositories import DailyReportRepository
from ai_agent.text_processing_pipeline import process_text_message, DEFAULT_EXCEL_PATH
from google_drive.google_drive_uploader import GoogleDriveUploader, Mode
from google_drive.utils import text_to_word_bytes, get_document_name, get_table_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@dataclass
class MessageDTO:
    chat_id: str
    chat_title: str
    user: str
    message_text: str
    time: str


message_counters = {}
drive_uploader = GoogleDriveUploader()


def save_message_as_word(
    text: str,
    sender_name: str,
    message_time: datetime,
    team_name: str,
) -> bool:
    try:
        if sender_name not in message_counters:
            message_counters[sender_name] = 0
        message_counters[sender_name] += 1

        filename = get_document_name(
            sender_name=sender_name,
            message_number=message_counters[sender_name],
            message_time=message_time,
        )

        word_bytes = text_to_word_bytes(text)

        team_folder_url = drive_uploader.url

        team_subfolder_url = drive_uploader.get_or_create_subfolder(
            team_folder_url, team_name
        )

        drive_uploader.upload_or_rewrite_file(
            team_subfolder_url or team_folder_url, filename, word_bytes, mode=Mode.W
        )
        logger.info(f"Saved message as Word document: {filename}")

        return True
    except Exception as e:
        logger.error(f"Error saving message as Word document: {e}")
        return False


def save_excel_report(excel_bytes: bytes, team_name: str) -> bool:
    try:
        filename = get_table_name(team_name=team_name)

        upload_url = drive_uploader.url

        drive_uploader.upload_or_rewrite_file(
            upload_url, filename, excel_bytes, mode=Mode.RW
        )
        logger.info(f"Saved Excel report: {filename}")

        return True
    except Exception as e:
        logger.error(f"Error saving Excel report: {e}")
        return False


def process_message(message: MessageDTO) -> bytes | None:
    logger.info(
        f"Received message for processing: chat_id={message.chat_id}, user={message.user}"
    )
    input_text = message.message_text
    input_date_str = message.time
    input_date = (
        datetime.strptime(input_date_str, "%d/%m/%Y, %H:%M:%S")
        if input_date_str
        else datetime.now()
    )

    if not isinstance(input_text, str) or not input_text.strip():
        logger.warning("Received message with empty or invalid text content.")
        return b""

    try:
        team_name = "SlovarikDB"
        sender_name = message.user or "UnknownUser"

        save_message_as_word(
            text=input_text,
            sender_name=sender_name,
            message_time=input_date,
            team_name=team_name,
        )
    except Exception as e:
        logger.error(
            f"Error initializing Google Drive uploader or saving Word document: {e}"
        )

    excel_log_path = DEFAULT_EXCEL_PATH
    excel_bytes = process_text_message(
        text=input_text, message_date=input_date.date(), excel_path=excel_log_path
    )

    if excel_bytes:
        logger.info(
            f"Successfully processed message and generated Excel ({len(excel_bytes)} bytes)."
        )

        if drive_uploader:
            try:
                team_name = "SlovarikDB"
                save_excel_report(
                    excel_bytes=excel_bytes,
                    team_name=team_name,
                )
            except Exception as e:
                logger.error(f"Error saving Excel report to Google Drive: {e}")

        return excel_bytes
    else:
        logger.error(
            f"Text processing failed or produced no data for message text: '{input_text[:100]}...'"
        )
        return None


def _callback(ch, method, properties, body):
    message = body.decode()
    message = json.loads(message)
    message_dto = MessageDTO(**message)

    logger.info(message_dto)

    if report := process_message(message_dto):
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
