import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatMessage, DailyReport


logger = logging.getLogger(__name__)


class DailyReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_report(self, chat_id: str, date: datetime.date) -> bytes:
        stmt = select(DailyReport.report).where(
            DailyReport.chat_id == chat_id,
            DailyReport.date == date,
        )
        res = await self.db.execute(stmt)
        return res.scalar()


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(
        self,
        chat_id: int,
        chat_title: str,
        user_id: int,
        user_name: str,
        message_text: str,
    ) -> None:
        message = ChatMessage(
            chat_id=str(chat_id),
            chat_title=chat_title,
            user_id=user_id,
            user_name=user_name,
            message_text=message_text,
        )
        self.db.add(message)
        await self.db.commit()
