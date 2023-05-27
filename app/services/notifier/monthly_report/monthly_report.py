from datetime import datetime
import os
from aiogram import Bot
from aiogram.types import FSInputFile
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO, ShiftDAO
from app.services.database.dao.shifts_difference import ShiftsDifferenceDAO
from app.services.database.dao.shift_check import ShiftCheckDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import ManualStartType
from app.services.database.models.shift import Shift
from app.services.database.models.shift_check import ShiftCheck
from app.services.database.models.user import User
from app.services.notifier.base import Notifier


class MonthlyReportNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, MailingType.MONTHLY_REPORT, None)
        self._shiftdao = ShiftDAO(session)
        self._userdao = UserDAO(session)
        self._shiftcheckdao = ShiftCheckDAO(session)
        self._manualstartdao = ManualStartDAO(session)
        self._shiftdiffdao = ShiftsDifferenceDAO(session)
        self._openshiftdao = OpenShiftDAO(session)
        self._closeshiftdao = CloseShiftDAO(session)

    async def get_objects_to_notify(self) -> list:
        shifts = await self._shiftdao.get_monthly_unreported()
        reports_rows: list[dict] = []
        for shift in shifts:
            await self._shiftdao.make_monthly_reported(shift)
            shift_check: ShiftCheck = await self._shiftcheckdao.get_by_id(shift.id)  # type: ignore
            if shift_check is None:
                continue
            shift_info = await self.get_shift_info(shift)
            reports_rows.append(shift_info)

        return [self.create_monthly_report(reports_rows)]

    async def get_shift_info(self, shift: Shift) -> dict:
        shift_check: ShiftCheck = await self._shiftcheckdao.get_by_id(shift.id)  # type: ignore
        operator: User = await self._userdao.get_by_id(shift.opened_by_id)  # type: ignore
        fine = await self.get_fine(shift, shift_check)
        salary = await self._userdao.get_salary(operator)
        info = {}

        info["Оператор"] = await self._userdao.get_user_name_by_id(shift.opened_by_id)
        info["Дата открытия смены"] = shift.open_date
        info["Дата закрытия смены"] = shift.close_date
        info["Ожидаемое кол-во денег"] = shift_check.money_expected
        info["Фактическое кол-во денег"] = shift_check.money_actual
        info["Недосдача"] = shift_check.money_difference
        info["Зарплата"] = salary
        info["Штраф"] = fine
        info["Итог за день"] = salary - fine
        return info

    async def get_fine(self, shift: Shift, shift_check: ShiftCheck):
        fine = shift_check.money_difference if shift_check.money_difference > 0 else 0
        fine += await self.get_fine_from_maual_starts(shift)
        if fine < 0:
            return 0
        return fine

    async def get_fine_from_maual_starts(self, shift: Shift) -> int:
        manual_starts = await self._manualstartdao.get_alerted_between_time(
            shift.open_date, shift.close_date
        )
        fine = 0
        for manual_start in manual_starts:
            if manual_start.type in [ManualStartType.TEST, ManualStartType.SERVICE]:
                continue
            if manual_start.mode is None:
                continue

            fine += self.get_fine_by_mode(manual_start.mode)
        return fine

    def get_fine_by_mode(self, mode: int):
        match mode:
            case 1:
                return 250
            case 2:
                return 450
            case 3:
                return 550
            case 4:
                return 650
            case _:
                return 0

    def create_monthly_report(self, report_rows: list):
        df = pd.DataFrame(data=report_rows)
        date = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        name = f"monthly_report_{date}.xlsx"
        path = "./monthly_reports/"
        df.to_excel(path + name)
        return path + name

    async def make_notified(self, object) -> None:
        pass

    async def send_notify(self, id: int, report_path: str) -> None:
        report = FSInputFile(report_path, filename="Полумесячный отчёт.xlsx")
        await self._bot.send_document(id, document=report)
