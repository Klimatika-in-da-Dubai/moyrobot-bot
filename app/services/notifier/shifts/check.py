from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.shift import ShiftDAO
from app.services.database.dao.shift_check import ShiftCheckDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.shift_check import ShiftCheck
from app.services.notifier.base import Notifier

from app.utils.text import escape_chars


class ShiftCheckNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        super().__init__(bot, session, MailingType.SHIFT_CHECK, ShiftCheckDAO(session))
        self._dao: ShiftCheckDAO
        self._shiftdao = ShiftDAO(session)

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, shift_check: ShiftCheck):
        await self._dao.make_notified(shift_check)

    def get_text(self, shift_check: ShiftCheck):  # type: ignore
        return (
            f"Проверка смены\n"
            f"*ID смены:* {shift_check.id}\n"
            f"*Разница в кассе:* {escape_chars(str(shift_check.money_difference))}"
        )

    @override
    async def send_notify(self, id: int, shift_check: ShiftCheck) -> None:
        text = self.get_text(shift_check)
        await self._bot.send_message(id, text)
