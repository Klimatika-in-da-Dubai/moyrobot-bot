import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.models.manual_start import (
    ManualStart,
    ManualStartType,
    RewashManualStart,
)
from app.services.notifier.manual_start.senders.sender import (
    TypedManualStartSender,
)
from app.services.notifier.utils import get_manual_start_mode_text
from app.utils.text import escape_chars


class RewashManualStartSender(TypedManualStartSender):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, ManualStartType.REWASH)

    def get_text(self, manual_start: ManualStart, typed_manual_start: RewashManualStart):  # type: ignore
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Перемывка\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Режим:* {escape_chars(get_manual_start_mode_text(manual_start))}\n"
            f"*Причина:* {escape_chars(typed_manual_start.description)}"
        )

    @override
    async def send(
        self, id: int, manual_start: ManualStart, typed_manual_start: RewashManualStart
    ):
        text = self.get_text(manual_start, typed_manual_start)
        try:
            await self._bot.send_photo(
                id, photo=typed_manual_start.photo_file_id, caption=text
            )
        except Exception:
            logging.error("Can't send report to chat with id %s", id)
