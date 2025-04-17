import datetime
import logging

from sqlalchemy.orm import Session

from db.models import DailyReport


logger = logging.getLogger(__name__)


class DailyReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_daily_report(
        self, chat_id: str, date: datetime.date, report: bytes
    ) -> None:
        if (
            existing_report := self.db.query(DailyReport)
            .filter_by(chat_id=chat_id, date=date)
            .one_or_none()
        ):
            existing_report.report = report
        else:
            report = DailyReport(
                chat_id=chat_id,
                date=date,
                report=report,
            )
            self.db.add(report)
        self.db.commit()
