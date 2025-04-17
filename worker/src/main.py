import json
import logging
import os
from datetime import datetime, date
from typing import Dict

import pika

from configs.config import settings
from db.base import session_factory
from db.repositories import DailyReportRepository
from ai_agent.text_processing_pipeline import process_text_message, DEFAULT_EXCEL_PATH
from google_drive.google_drive_uploader import GoogleDriveUploader
from google_drive.utils import text_to_word_bytes, get_document_name, get_table_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Track message count per sender
message_counters = {}

def save_message_as_word(text: str, sender_name: str, chat_id: int, message_time: datetime, drive_uploader: GoogleDriveUploader, team_name: str) -> bool:
    """
    Save message as a Word document in Google Drive with the required naming format.
    
    Args:
        text: Message text content
        sender_name: Name of the message sender
        chat_id: Chat ID where the message was received
        message_time: Timestamp of the message
        drive_uploader: Google Drive uploader instance
        team_name: Name of the team
        
    Returns:
        bool: Whether the operation was successful
    """
    try:
        # Update message counter for this sender
        if sender_name not in message_counters:
            message_counters[sender_name] = 0
        message_counters[sender_name] += 1
        
        # Generate filename using the utility function
        filename = get_document_name(
            sender_name=sender_name,
            message_number=message_counters[sender_name],
            message_time=message_time
        )
        
        # Convert text to Word document bytes
        word_bytes = text_to_word_bytes(text)
        
        # Create team folder if it doesn't exist
        team_folder_url = drive_uploader.url
        
        # Try to create the team folder (if it exists, we'll catch the exception)
        try:
            team_subfolder_url = drive_uploader.create_subfolder(team_folder_url, team_name)
            logger.info(f"Created new team folder: {team_name}")
        except Exception as e:
            logger.warning(f"Team folder may already exist or couldn't be created: {e}")
            # Use the subfolder URL that was saved during initialization
            team_subfolder_url = drive_uploader.subfolder_url
        
        # Upload Word document to the team folder
        drive_uploader.upload_file(team_subfolder_url or team_folder_url, filename, word_bytes)
        logger.info(f"Saved message as Word document: {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving message as Word document: {e}")
        return False

def save_excel_report(excel_bytes: bytes, drive_uploader: GoogleDriveUploader, team_name: str) -> bool:
    """
    Save Excel report to Google Drive with the required naming format.
    
    Args:
        excel_bytes: Excel file content as bytes
        drive_uploader: Google Drive uploader instance
        team_name: Name of the team
        
    Returns:
        bool: Whether the operation was successful
    """
    try:
        # Generate filename using the utility function
        filename = get_table_name(team_name=team_name)
        
        # Use the team folder URL - either the main folder or the subfolder
        team_folder_url = drive_uploader.url
        team_subfolder_url = drive_uploader.subfolder_url
        
        # Upload Excel file to the team folder
        upload_url = team_subfolder_url or team_folder_url
        drive_uploader.upload_file(upload_url, filename, excel_bytes)
        logger.info(f"Saved Excel report: {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving Excel report: {e}")
        return False

def some_magic(message: Dict[str, str | int]) -> bytes | None:
    """ 
    Processes the message text using the AI agent, updates an Excel log, 
    and returns the updated Excel file as bytes.
    """ 
    logger.info(f"Received message for processing: chat_id={message.get('chat_id')}, user={message.get('user')}")
    input_text = message.get("message", "")
    input_date_str = message.get("time", None)
    input_date = datetime.strptime(input_date_str, "%d/%m/%Y, %H:%M:%S") if input_date_str else datetime.now()
    
    if not isinstance(input_text, str) or not input_text.strip():
        logger.warning("Received message with empty or invalid text content.")
        return b""
    
    drive_uploader = None
    # Initialize Google Drive uploader
    try:
        drive_uploader = GoogleDriveUploader()
        
        # Save message as Word document
        team_name = os.environ.get("TEAM_NAME", "AgroTeam")  # Replace with actual team name
        sender_name = message.get("user", "UnknownUser")
        chat_id = message.get("chat_id", 0)
        
        save_message_as_word(
            text=input_text,
            sender_name=sender_name,
            chat_id=chat_id,
            message_time=input_date,
            drive_uploader=drive_uploader,
            team_name=team_name
        )
    except Exception as e:
        logger.error(f"Error initializing Google Drive uploader or saving Word document: {e}")

    excel_log_path = DEFAULT_EXCEL_PATH
    excel_bytes = process_text_message(text=input_text, message_date=input_date.date(), excel_path=excel_log_path)
    
    if excel_bytes:
        logger.info(f"Successfully processed message and generated Excel ({len(excel_bytes)} bytes).")
        
        # Save Excel report to Google Drive
        if drive_uploader:
            try:
                team_name = os.environ.get("TEAM_NAME", "AgroTeam")
                save_excel_report(
                    excel_bytes=excel_bytes,
                    drive_uploader=drive_uploader,
                    team_name=team_name
                )
            except Exception as e:
                logger.error(f"Error saving Excel report to Google Drive: {e}")
            
        return excel_bytes
    else:
        logger.error(f"Text processing failed or produced no data for message text: '{input_text[:100]}...'")
        return None


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
