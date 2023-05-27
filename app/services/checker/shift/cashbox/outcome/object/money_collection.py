from typing import Sequence
from app.services.checker.shift.cashbox.outcome.object.object import OutcomeObject
from app.services.database.dao.money_collection import MoneyCollectionDAO
from app.services.database.models.money_collection import MoneyCollection
from app.services.database.models.shift import Shift


class MoneyCollectionOutcome(OutcomeObject):
    def __init__(self, session):
        super().__init__(MoneyCollectionDAO(session))
        self.dao: MoneyCollectionDAO

    async def get_outcome(self, shift: Shift):
        result: Sequence[
            MoneyCollection
        ] = await self.dao.get_money_collection_between_time(
            shift.open_date, shift.close_date
        )
        return sum([el.money_amount for el in result])
