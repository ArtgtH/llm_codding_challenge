import asyncio
import logging
from datetime import datetime
from typing import Dict

import pytz
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError
from aiogram.types import BufferedInputFile

from db.base import async_session_factory
from db.repositories import DailyReportRepository


logger = logging.getLogger(__name__)


class ChatTimers:
    def __init__(self, bot: Bot):
        self.timers: Dict[int, asyncio.Task] = {}
        self.lock = asyncio.Lock()
        self.bot = bot

    async def reset_timer(self, chat_id: int):
        async with self.lock:
            task = self.timers.get(chat_id)
            if task:
                task.cancel()

            new_task = asyncio.create_task(self._timer_task(chat_id))
            self.timers[chat_id] = new_task

    async def _timer_task(self, chat_id: int):
        current_task = asyncio.current_task()
        try:
            logger.info("Started timer")
            await asyncio.sleep(120)
            logger.info("Finished timer")

            async with async_session_factory() as db:
                report = await DailyReportRepository(db).get_daily_report(
                    str(chat_id), datetime.today().date()
                )

            if report is None:
                logger.warning("No report found")
                return

            report_datetime = datetime.now(pytz.timezone("Europe/Moscow"))
            filename = f"{report_datetime.hour}_{report_datetime.day}_{report_datetime.month}_{report_datetime.year}_SlovarikDB.xlsx"
            input_file = BufferedInputFile(report, filename=filename)

            await self.bot.send_document(chat_id, document=input_file)

        except (TelegramAPIError, TelegramRetryAfter) as e:
            logger.warning(f"Telegram API error: {e}")
        except Exception as e:
            logger.error(f"Timer error: {e}")
        finally:
            async with self.lock:
                if self.timers.get(chat_id) is current_task:
                    self.timers.pop(chat_id)
