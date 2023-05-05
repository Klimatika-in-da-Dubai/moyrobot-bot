import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.models.manual_start import (
    ManualStartType,
    RewashManualStart,
)
from app.services.notifier.manual_start.senders.sender import TypedManualStartSender
from app.utils.text import escape_chars


class RewashManualStartSender(TypedManualStartSender):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, ManualStartType.REWASH)

    def get_text(self, manual_start: RewashManualStart):  # type: ignore
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Перемывка\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Причина:* {escape_chars(manual_start.description)}"
        )

    @override
    async def send(self, id: int, manual_start: RewashManualStart):
        text = self.get_text(manual_start)
        try:
            await self._bot.send_photo(
                id, photo=manual_start.photo_file_id, caption=text
            )
        except Exception:
            logging.error("Can't send report to chat with id %s", id)
