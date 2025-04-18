import pytz
from docx import Document
from io import BytesIO
from datetime import datetime


def text_to_word_bytes(text: str) -> bytes:
    doc = Document()

    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph)

    buffer = BytesIO()
    doc.save(buffer)

    return buffer.getvalue()


def get_table_name(team_name: str = "AgroTeam") -> str:
    current_time = datetime.now(pytz.timezone("Europe/Moscow"))
    time_format = current_time.strftime("%H_%d_%m_%Y")
    return f"{time_format}_{team_name}.xlsx"


def get_document_name(
    sender_name: str, message_number: int, message_time: datetime
) -> str:
    time_format = message_time.strftime("%M_%H_%d_%m_%Y")
    return f"{sender_name}_{message_number}_{time_format}.docx"
