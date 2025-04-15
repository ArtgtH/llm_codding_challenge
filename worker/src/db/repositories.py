import datetime
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import DailyReport


logger = logging.getLogger(__name__)


class DailyReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_daily_report(
        self, chat_id: str, date: datetime.date, report: bytes
    ) -> None:
        try:
            report = DailyReport(
                chat_id=chat_id,
                date=date,
                report=report,
            )
            logger.info(f"Create daily report {report}")
            self.db.add(report)
            self.db.commit()
        except IntegrityError:
            logger.error("Report constraint `uq_chat_id_date`")
