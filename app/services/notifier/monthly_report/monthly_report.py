from datetime import datetime
from aiogram import Bot
from aiogram.types import FSInputFile
import os
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.dao.cleaning import CleaningDAO
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
from UliPlot.XLSX import auto_adjust_xlsx_column_width
from app.utils.calendar_names import month_name


class MonthlyReportNotifier(Notifier):
    def __init__(self, bot, session):
        super().__init__(bot, session, MailingType.MONTHLY_REPORT, None)
        self._shiftdao = ShiftDAO(session)
        self._userdao = UserDAO(session)
        self._shiftcheckdao = ShiftCheckDAO(session)
        self._manualstartdao = ManualStartDAO(session)
        self._shiftdiffdao = ShiftsDifferenceDAO(session)
        self._openshiftdao = OpenShiftDAO(session)
        self._closeshiftdao = CloseShiftDAO(session)
        self._cleaningdao = CleaningDAO(session)

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
        if shift_check is None:
            raise ValueError("shift_check is None")

        operator: User = await self._userdao.get_by_id(shift.opened_by_id)  # type: ignore

        salary = await self._userdao.get_salary(operator)

        salary = 0 if salary is None else salary

        money_check_difference = shift_check.money_difference
        manual_starts_fine = await self.get_fine_from_maual_starts(shift)
        cleaning_fine = await self.get_fine_for_cleaning(shift, salary)
        fine = 2 * manual_starts_fine + cleaning_fine

        if money_check_difference < 0:
            fine += 2 * money_check_difference
        info = {}

        info["Оператор"] = operator.name
        info["Дата"] = shift.open_date.date()
        info["Время открытия"] = shift.open_date.time().strftime("%H:%M:%S")
        info["Время закрытия"] = shift.close_date.time().strftime("%H:%M:%S")
        info["Смена"] = self.get_shift_type(shift)
        info["Оклад"] = salary
        info["Плановая"] = shift_check.money_expected
        info["Фактическое"] = shift_check.money_actual
        info["Не сошлась наличка"] = money_check_difference
        info["Нет отчёта"] = manual_starts_fine
        info["Уборка"] = cleaning_fine
        info["Штраф"] = fine
        info["Итого"] = salary + fine
        return info

    def get_shift_type(self, shift: Shift) -> str:
        return "День" if shift.open_date.time() <= shift.close_date.time() else "Ночь"

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
                return -250
            case 2:
                return -450
            case 3:
                return -550
            case 4:
                return -650
            case _:
                return 0

    async def get_fine_for_cleaning(self, shift: Shift, salary: int) -> float:
        cleanings = await self._cleaningdao.get_cleanings_between_time(
            shift.open_date, shift.close_date
        )

        if any([cleaning.approved in (None, True) for cleaning in cleanings]):
            return 0

        return -salary * 0.15

    def create_monthly_report(self, report_rows: list):
        df = pd.DataFrame(data=report_rows)
        name = "monthly_report.xlsx"
        path = "./reports/"
        with pd.ExcelWriter(path + name) as writer:  # pyright: ignore
            df.to_excel(writer, index=False, sheet_name="MySheet")
            auto_adjust_xlsx_column_width(df, writer, sheet_name="MySheet", margin=1)
        return path + name

    async def send_notify(self, id: int, report_path: str) -> None:
        match datetime.today().day:
            case 1:
                filename = f"Зарплата {month_name[datetime.today().month - 1]}.xlsx"
            case 16:
                filename = f"Aванс {month_name[datetime.today().month]}.xlsx"
            case _:
                filename = "Полумесячный отчёт.xlsx"
        report = FSInputFile(report_path, filename=filename)
        await self._bot.send_document(id, document=report)

    async def after_sending(self, report_path: str):
        os.remove(report_path)
