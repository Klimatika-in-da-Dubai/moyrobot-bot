from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing_extensions import override

from app.services.database.dao.shift import ShiftDAO
from app.services.database.dao.shifts_difference import ShiftsDifferenceDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.shifts_difference import ShiftsDifference
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class ShiftDifferenceNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        super().__init__(
            bot, session, MailingType.SHIFTS_DIFFERENCE, ShiftsDifferenceDAO(session)
        )
        self._dao: ShiftsDifferenceDAO
        self._shiftdao = ShiftDAO(session)

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, shifts_difference: ShiftsDifference):
        await self._dao.make_notified(shifts_difference)

    def get_text(self, shifts_difference: ShiftsDifference):  # type: ignore
        return (
            f"Разница закрытия\\-открытия смен\n"
            f"*ID закрытой смены:* {shifts_difference.closed_shift_id}\n"
            f"*ID открытой смены:* {shifts_difference.opened_shift_id}\n"
            f"*Разница в кассе:* {escape_chars(str(shifts_difference.money_difference))}"
        )

    @override
    async def send_notify(self, id: int, shifts_difference: ShiftsDifference) -> None:
        text = self.get_text(shifts_difference)
        await self._bot.send_message(id, text)
