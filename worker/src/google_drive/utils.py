from docx import Document
from io import BytesIO
from datetime import datetime

def text_to_word_bytes(text: str) -> bytes:
    """
    Convert a text string to a Word document (bytes).

    Args:
        text: Input text to be saved in the Word document

    Returns:
        bytes: Bytes of the generated Word document
    """
    doc = Document()

    for paragraph in text.split('\n'):
        doc.add_paragraph(paragraph)

    buffer = BytesIO()
    doc.save(buffer)

    return buffer.getvalue()

def get_table_name(team_name: str = "AgroTeam") -> str:
    """
    Generate Excel table filename according to the requirements.
    Format: "ЧасДеньМесяцГод_НазваниеКоманды"
    
    Args:
        team_name: Name of the team
        
    Returns:
        str: Filename for the Excel table
    """
    current_time = datetime.now()
    time_format = current_time.strftime("%H%d%m%Y")
    return f"{time_format}_{team_name}.xlsx"

def get_document_name(sender_name: str, message_number: int, message_time: datetime) -> str:
    """
    Generate Word document filename according to the requirements.
    Format: "ИмяОтправителя_Номер-сообщения_МинутаЧасДеньМесяцГод"
    
    Args:
        sender_name: Name of the message sender
        message_number: Sequence number of the message from this sender
        message_time: Timestamp of the message
        
    Returns:
        str: Filename for the Word document
    """
    time_format = message_time.strftime("%M%H%d%m%Y")
    return f"{sender_name}_{message_number}_{time_format}.docx"


