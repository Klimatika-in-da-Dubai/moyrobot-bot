import asyncio

from app.services.checker.shift.cashbox.outcome.object.object import OutcomeObject
from app.services.database.models.shift import Shift


class OutcomeGetter:
    def __init__(self, outcome_objects: list[OutcomeObject]):
        self.outcome_objects = outcome_objects

    async def get_outcome(self, shift: Shift) -> int:
        tasks = [
            asyncio.create_task(obj.get_outcome(shift)) for obj in self.outcome_objects
        ]
        outcomes = await asyncio.gather(*tasks)
        return sum(outcomes)
