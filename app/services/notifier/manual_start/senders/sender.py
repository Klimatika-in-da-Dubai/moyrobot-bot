from abc import abstractmethod
from aiogram import Bot

from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import ManualStart, ManualStartType


class TypedManualStartSender:
    def __init__(self, bot: Bot, session: async_sessionmaker, type: ManualStartType):
        self._bot = bot
        self._dao: ManualStartDAO = ManualStartDAO(session)
        self._type = type

    async def send_notify(self, id: int, manual_start: ManualStart):
        typed_manual_start = await self.get_typed_manual_start(manual_start)
        await self.send(id, typed_manual_start)

    async def get_typed_manual_start(self, manual_start: ManualStart):
        return await self._dao.get_typed_manual_start(manual_start.id, self._type)

    @abstractmethod
    async def send(self, id: int, manual_start):
        pass
