from abc import abstractmethod
import logging
from aiogram import Bot

from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.mailing import get_mailing_ids
from app.services.database.models.mailing import MailingType


class Notifier:
    def __init__(
        self, bot: Bot, session: async_sessionmaker, mailing_type: MailingType, dao
    ):
        self._bot = bot
        self._session = session
        self._mailing_type = mailing_type
        self._dao = dao

    async def notify(self) -> None:
        objects_to_notify = await self.get_objects_to_notify()
        ids = await self.get_notify_ids()
        for obj in objects_to_notify:
            await self.make_notified(obj)
            for id in ids:
                try:
                    await self.send_notify(id, obj)
                except Exception as e:
                    logging.error("Can't send notify to user with id = %s", id)
                    logging.error("Exception: %s", e)

    @abstractmethod
    async def get_objects_to_notify(self) -> list:
        ...

    @abstractmethod
    async def make_notified(self, object) -> None:
        ...

    @abstractmethod
    async def send_notify(self, id: int, object) -> None:
        ...

    async def get_notify_ids(self) -> list:
        return await get_mailing_ids(self._session, self._mailing_type)
