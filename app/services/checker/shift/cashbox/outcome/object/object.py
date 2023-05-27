from abc import ABC, abstractmethod

from app.services.database.models.shift import Shift


class OutcomeObject(ABC):
    def __init__(self, dao):
        self.dao = dao

    @abstractmethod
    async def get_outcome(self, shift: Shift):
        ...
