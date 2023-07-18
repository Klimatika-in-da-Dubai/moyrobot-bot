from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.shift import OpenShiftDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.shift import OpenShift
from app.services.notifier.base import Notifier
from app.services.notifier.shifts.difference import ShiftDifferenceNotifier
from app.services.notifier.shifts.utils import get_text


class OpenShiftNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        after_notifiers = [ShiftDifferenceNotifier(bot, session)]
        super().__init__(
            bot,
            session,
            MailingType.SHIFT,
            OpenShiftDAO(session),
            after_notifiers=after_notifiers,
        )
        self._dao: OpenShiftDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, shift: OpenShift):
        await self._dao.make_notified(shift)

    @override
    async def send_notify(self, id: int, shift: OpenShift) -> None:
        text = get_text(shift)
        await self._bot.send_message(id, text)
