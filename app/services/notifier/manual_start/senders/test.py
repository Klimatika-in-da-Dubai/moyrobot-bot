import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.models.manual_start import (
    ManualStart,
    ManualStartType,
    TestManualStart,
)
from app.services.notifier.manual_start.senders.sender import TypedManualStartSender
from app.utils.text import escape_chars


class TestManualStartSender(TypedManualStartSender):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, ManualStartType.TEST)

    def get_text(self, manual_start: ManualStart, typed_manual_start: TestManualStart):  # type: ignore
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Тест\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Режим:* {escape_chars(str(manual_start.mode))}\n"
            f"*Причина:* {escape_chars(typed_manual_start.description)}"
        )

    @override
    async def send(
        self, id: int, manual_start: ManualStart, typed_manual_start: TestManualStart
    ):
        text = self.get_text(manual_start, typed_manual_start)
        try:
            await self._bot.send_message(id, text=text)
        except Exception:
            logging.error("Can't send report to chat with id %s", id)
