from datetime import date

from sqlalchemy import LargeBinary, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    chat_id: Mapped[str]
    report: Mapped[bytes] = mapped_column(LargeBinary)

    __table_args__ = (UniqueConstraint("chat_id", "date", name="uq_chat_id_date"),)
