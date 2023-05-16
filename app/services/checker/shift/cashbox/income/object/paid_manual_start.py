from typing import Sequence
from app.services.checker.shift.cashbox.income.object.object import IncomeObject
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import ManualStartType, PaidManualStart
from app.services.database.models.shift import Shift
from app.services.database.models.utils import PaymentMethod


class PaidManualStartIncome(IncomeObject):
    def __init__(self, session):
        super().__init__(ManualStartDAO(session))
        self.dao: ManualStartDAO

    async def get_income(self, shift: Shift):
        result: Sequence[PaidManualStart] = await self.dao.get_typed_between_time(
            ManualStartType.PAID, shift.open_date, shift.close_date
        )
        return sum(
            [
                el.payment_amount
                for el in filter(
                    lambda x: x.payment_method == PaymentMethod.CASH, result
                )
            ]
        )
