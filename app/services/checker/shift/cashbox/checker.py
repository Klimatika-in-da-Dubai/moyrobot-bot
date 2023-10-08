from sqlalchemy.ext.asyncio import AsyncSession
from app.services.checker.shift.cashbox.income.getter import IncomeGetter
from app.services.checker.shift.cashbox.income.object.paid_manual_start import (
    PaidManualStartIncome,
)
from app.services.checker.shift.cashbox.outcome.getter import OutcomeGetter
from app.services.checker.shift.cashbox.outcome.object.money_collection import (
    MoneyCollectionOutcome,
)
from app.services.checker.shift.checker import Checker
from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO
from app.services.database.models.shift import CloseShift, OpenShift, Shift
from app.services.database.models.shift_check import ShiftCheck


class CashboxChecker(Checker):
    def __init__(self, session: AsyncSession):
        self.income_getter = IncomeGetter([PaidManualStartIncome(session)])
        self.outcome_getter = OutcomeGetter([MoneyCollectionOutcome(session)])
        self.openshiftdao = OpenShiftDAO(session)
        self.closeshiftdao = CloseShiftDAO(session)

    async def check(self, shift: Shift, shift_check: ShiftCheck):
        open_shift: OpenShift = await self.openshiftdao.get_by_id(shift.id)  # type: ignore
        close_shift: CloseShift = await self.closeshiftdao.get_by_id(shift.id)  # type: ignore

        cashbox_start = open_shift.money_amount
        cashbox_end = close_shift.money_amount

        shift_check.money_expected = cashbox_start + await self.get_cashbox_diff(shift)
        shift_check.money_actual = cashbox_end
        shift_check.money_difference = (
            shift_check.money_actual - shift_check.money_expected
        )

    async def get_cashbox_diff(self, shift: Shift) -> int:
        income = await self.income_getter.get_income(shift)
        outcome = await self.outcome_getter.get_outcome(shift)
        return income - outcome
