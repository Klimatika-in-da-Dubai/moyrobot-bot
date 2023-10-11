from typing import Sequence
from app.services.checker.shift.cashbox.income.object.object import IncomeObject
from app.services.database.dao.cashbox_replenishment import CashboxReplenishmentDAO
from app.services.database.models.cashbox_replenishment import CashboxReplenishment
from app.services.database.models.shift import Shift


class CashboxReplenishmentIncome(IncomeObject):
    def __init__(self, session):
        super().__init__(CashboxReplenishmentDAO(session))
        self.dao: CashboxReplenishmentDAO

    async def get_income(self, shift: Shift):
        result: Sequence[
            CashboxReplenishment
        ] = await self.dao.get_cashbox_replenishment_between_time(
            shift.open_date, shift.close_date
        )
        return sum([el.money_amount for el in result])
