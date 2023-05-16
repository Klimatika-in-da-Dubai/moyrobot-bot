from abc import ABC, abstractmethod

from app.services.database.models.shift import Shift
from app.services.database.models.shift_check import ShiftCheck


class Checker(ABC):
    @abstractmethod
    async def check(self, shift: Shift, shift_check: ShiftCheck):
        ...
