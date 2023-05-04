from datetime import timedelta
from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import ManualStart
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class ManualStartReminder(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(
            bot,
            session,
            MailingType.MANUAL_START_REPORT_REMIND,
            ManualStartDAO(session),
        )
        self._dao: ManualStartDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unreminded(delay=timedelta(minutes=3))

    @override
    async def make_notified(self, manual_start: ManualStart) -> None:
        await self._dao.make_report_reminded(manual_start)

    def get_text(self, manual_start: ManualStart):
        date = escape_chars(manual_start.date.strftime("%Y\\-%m\\-%d %H:%M:%S"))

        return (
            "Не было получено отчёта по ручному запуску\n\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Дата\\-время:* {date} \n"
        )

    @override
    async def send_notify(self, id: int, manual_start: ManualStart):
        text = self.get_text(manual_start)
        await self._bot.send_message(id, text=text)
