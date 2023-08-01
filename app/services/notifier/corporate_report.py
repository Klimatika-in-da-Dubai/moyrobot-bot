from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from aiogram import Bot
from aiogram.types import FSInputFile
from apscheduler.job import Iterable
from sqlalchemy.ext.asyncio import async_sessionmaker
import pandas as pd
from app.services.database.dao.corporate_report import CorporateReportDAO
from app.services.database.dao.corporation import CorporationDAO
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.corporate_report import CorporateReport
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import (
    CorporateManualStart,
    ManualStart,
    ManualStartType,
)
from app.services.notifier.base import Notifier
from app.utils.calendar_names import month_name
from UliPlot.XLSX import auto_adjust_xlsx_column_width
import os


@dataclass
class CorporateReportNotify:
    corporate_report: CorporateReport
    path_to_file: Path


class CorporateReportNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(
            bot, session, MailingType.CORPORATE_REPORT, CorporateReportDAO(session)
        )

        self._dao: CorporateReportDAO
        self._manualstartdao = ManualStartDAO(session)
        self._corporationdao = CorporationDAO(session)

    async def get_objects_to_notify(self) -> list[CorporateReportNotify]:
        corporate_reports: list[CorporateReport] = await self._dao.get_unreported()
        return [await self.create_report(report) for report in corporate_reports]

    async def create_report(self, report: CorporateReport) -> CorporateReportNotify:
        rows = await self.get_corporate_report_rows(report)
        path_to_file = await self.create_xlsx_file(rows)

        return CorporateReportNotify(report, path_to_file)

    async def get_corporate_report_rows(self, report: CorporateReport) -> list[dict]:
        corporate_manual_starts = await self.get_corporate_manual_starts(report)
        return await self.get_rows(corporate_manual_starts)

    async def get_corporate_manual_starts(
        self, report: CorporateReport
    ) -> list[CorporateManualStart]:
        return list(
            await self._manualstartdao.get_typed_between_time(
                ManualStartType.CORPORATE, report.start, report.end
            )
        )

    async def get_rows(
        self, manual_starts: Iterable[CorporateManualStart]
    ) -> list[dict]:
        return [await self.get_row(manual_start) for manual_start in manual_starts]

    async def get_row(self, corporate_manual_start: CorporateManualStart) -> dict:
        manual_start = await self.get_untyped_manual_start(corporate_manual_start)

        date = manual_start.date.date()
        corporation = await self.get_corporation_name(corporate_manual_start)
        mode = self.get_mode(manual_start)
        return {
            "Дата": date,
            "Копрорация": corporation,
            "Режим": mode,
        }

    async def get_untyped_manual_start(
        self, manual_start: CorporateManualStart
    ) -> ManualStart:
        manual_start_untyped = await self._manualstartdao.get_by_id(manual_start.id)
        if manual_start_untyped is None:
            raise ValueError(f"No manual_start with id {manual_start.id}")

        return manual_start_untyped

    async def get_corporation_name(self, manual_start: CorporateManualStart) -> str:
        return await self._corporationdao.get_name(manual_start.corporation_id)

    def get_mode(self, manual_start: ManualStart) -> str | int:
        return manual_start.mode if manual_start.mode is not None else "Неизвестно"

    async def create_xlsx_file(self, rows: list[dict]) -> Path:
        df = pd.DataFrame(data=rows)
        path_to_file = Path("./reports/corporate_report_.xlsx")
        with pd.ExcelWriter(path_to_file) as writer:  # pyright: ignore
            df.to_excel(writer, index=False, sheet_name="MySheet")
            auto_adjust_xlsx_column_width(df, writer, sheet_name="MySheet", margin=0)
        return path_to_file

    async def make_notified(self, report: CorporateReportNotify) -> None:
        return await self._dao.make_reported(report.corporate_report)

    async def send_notify(self, id: int, report: CorporateReportNotify) -> None:
        input_file = self.get_input_file(report)
        await self._bot.send_document(id, document=input_file)

    def get_input_file(self, report: CorporateReportNotify) -> FSInputFile:
        filename = f"Корпоративные запуски {month_name[report.corporate_report.start.month]}.xlsx"
        return FSInputFile(path=report.path_to_file, filename=filename)

    async def after_sending(self, report: CorporateReportNotify):
        os.remove(report.path_to_file)
