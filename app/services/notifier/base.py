from abc import abstractmethod
import logging
from typing import Optional
from aiogram import Bot
from apscheduler.job import Iterable

from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.dao.mailing import get_mailing_ids
from app.services.database.models.mailing import MailingType


class Notifier:
    def __init__(
        self,
        bot: Bot,
        session: async_sessionmaker,
        mailing_type: MailingType,
        dao: Optional[BaseDAO],
        before_notifiers: Optional[Iterable["Notifier"]] = None,
        after_notifiers: Optional[Iterable["Notifier"]] = None,
    ):
        self._bot = bot
        self._session = session
        self._mailing_type = mailing_type
        self._dao = dao

        self._before_notifiers = []
        if before_notifiers is not None:
            self._before_notifiers = before_notifiers

        self._after_notifiers = []
        if after_notifiers is not None:
            self._after_notifiers = after_notifiers

    async def notify(self) -> None:
        await self.before_notify()
        await self._start_notify()
        await self.after_notify()

    async def _start_notify(self):
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

    async def use_notifiers(self, notifiers: Iterable["Notifier"]) -> None:
        for notifier in notifiers:
            await notifier.notify()

    async def before_notify(self):
        await self.use_notifiers(self._before_notifiers)
        await self.before()

    async def after_notify(self):
        await self.use_notifiers(self._after_notifiers)
        await self.after()

    @abstractmethod
    async def before(self):
        ...

    @abstractmethod
    async def after(self):
        ...

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
