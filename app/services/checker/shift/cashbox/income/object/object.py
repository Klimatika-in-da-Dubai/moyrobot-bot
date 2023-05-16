from abc import ABC, abstractmethod

from app.services.database.models.shift import Shift


class IncomeObject(ABC):
    def __init__(self, dao):
        self.dao = dao

    @abstractmethod
    async def get_income(self, shift: Shift):
        ...
