import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.corporation import CorporationDAO
from app.services.database.models.manual_start import (
    CorporateManualStart,
    ManualStart,
    ManualStartType,
)
from app.services.notifier.manual_start.senders.sender import TypedManualStartSender
from app.utils.text import escape_chars


class CorporateManualStartSender(TypedManualStartSender):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, ManualStartType.CORPORATE)
        self._corporationdao = CorporationDAO(session)

    async def get_text(self, manual_start: ManualStart, typed_manual_start: CorporateManualStart):  # type: ignore
        corporation_name = await self._corporationdao.get_name(
            typed_manual_start.corporation_id
        )
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Перемывка\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Компания:* {escape_chars(corporation_name)}\n"
            f"*Причина:* {escape_chars(typed_manual_start.description)}"
        )

    @override
    async def send(
        self,
        id: int,
        manual_start: ManualStart,
        typed_manual_start: CorporateManualStart,
    ):
        text = await self.get_text(manual_start, typed_manual_start)
        try:
            await self._bot.send_photo(
                id, photo=typed_manual_start.photo_file_id, caption=text
            )
        except Exception:
            logging.error("Can't send report to chat with id %s", id)
