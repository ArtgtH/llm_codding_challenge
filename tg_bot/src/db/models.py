from datetime import datetime

from sqlalchemy import DateTime, String, Integer, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ChatMessage(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(primary_key=True)
	chat_id: Mapped[str]
	chat_title: Mapped[str] = mapped_column(String(255))
	user_id: Mapped[int]
	user_name: Mapped[str] = mapped_column(String(255))
	message_text: Mapped[str]
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DailyReport(Base):
	__tablename__ = "daily_reports"

	id: Mapped[int] = mapped_column(primary_key=True)
	date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	chat_id: Mapped[str]
	report: Mapped[bytes] = mapped_column(LargeBinary)

	__table_args__ = (
		UniqueConstraint("chat_id", "date", name="uq_chat_id_date"),
	)

