import asyncio

from app.services.checker.shift.cashbox.income.object.object import IncomeObject
from app.services.database.models.shift import Shift


class IncomeGetter:
    def __init__(self, income_objects: list[IncomeObject]):
        self.income_objects = income_objects

    async def get_outcome(self, shift: Shift) -> int:
        tasks = [
            asyncio.create_task(obj.get_income(shift)) for obj in self.income_objects
        ]
        incomes = await asyncio.gather(*tasks)
        return sum(incomes)
