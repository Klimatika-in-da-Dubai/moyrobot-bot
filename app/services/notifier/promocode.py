from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.promocode import PromocodeDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.promocode import Promocode
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars, format_phone


class PromocodeNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        super().__init__(bot, session, MailingType.PROMOCODE, PromocodeDAO(session))
        self._dao: PromocodeDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, promocode: Promocode):
        await self._dao.make_notified(promocode)

    def get_text(self, promocode: Promocode):
        phone = escape_chars(format_phone(promocode.phone))
        wash_mode = promocode.wash_mode
        description = escape_chars(promocode.description)

        return (
            f"Выдать промокод\n\n"
            f"*Телефон:* {phone}\n"
            f"*Режим:* {wash_mode}\n"
            f"*Причина:* {description}\n"
        )

    @override
    async def send_notify(self, id: int, promocode: Promocode) -> None:
        text = self.get_text(promocode)
        await self._bot.send_message(id, text=text)
