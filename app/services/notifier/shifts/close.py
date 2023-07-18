from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.shift import CloseShiftDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.shift import CloseShift
from app.services.notifier.base import Notifier
from app.services.notifier.shifts.check import ShiftCheckNotifier
from app.services.notifier.shifts.utils import get_text


class CloseShiftNotifier(Notifier):
    def __init__(
        self,
        bot: Bot,
        session: async_sessionmaker,
    ) -> None:
        after_notifiers = [ShiftCheckNotifier(bot, session)]
        super().__init__(
            bot,
            session,
            MailingType.SHIFT,
            CloseShiftDAO(session),
            after_notifiers=after_notifiers,
        )
        self._dao: CloseShiftDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, shift: CloseShift):
        await self._dao.make_notified(shift)

    @override
    async def send_notify(self, id: int, shift: CloseShift) -> None:
        text = get_text(shift)
        await self._bot.send_message(id, text)

    @override
    async def before_notify(self):
        return await super().before_notify()
