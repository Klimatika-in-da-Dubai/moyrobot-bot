import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.models.manual_start import (
    ManualStartType,
    ServiceManualStart,
)
from app.services.notifier.manual_start.senders.sender import TypedManualStartSender
from app.utils.text import escape_chars


class ServiceManualStartSender(TypedManualStartSender):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, ManualStartType.SERVICE)

    def get_text(self, manual_start: ServiceManualStart):  # type: ignore
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Технический\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Причина:* {escape_chars(manual_start.description)}"
        )

    @override
    async def send(self, id: int, manual_start: ServiceManualStart):
        text = self.get_text(manual_start)
        try:
            await self._bot.send_message(id, text=text)
        except Exception:
            logging.error("Can't send report to chat with id %s", id)