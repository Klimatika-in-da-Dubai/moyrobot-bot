from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.bonus import BonusDAO
from app.services.database.models.bonus import Bonus

from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import format_phone, escape_chars


class BonusNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        super().__init__(bot, session, MailingType.BONUS, BonusDAO(session))
        self._dao: BonusDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, bonus: Bonus):
        await self._dao.make_notified(bonus)

    def get_text(self, bonus: Bonus):
        phone = escape_chars(format_phone(bonus.phone))
        bonus_amount = bonus.bonus_amount
        description = escape_chars(bonus.description)

        return (
            "Начисление бонусов\n\n"
            f"*Телефон:* {phone}\n"
            f"*Количество бонусов:* {bonus_amount}\n"
            f"*Причина:* {description}\n"
        )

    @override
    async def send_notify(self, id: int, bonus: Bonus) -> None:
        text = self.get_text(bonus)
        await self._bot.send_message(id, text=text)
