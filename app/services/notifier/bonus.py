from collections.abc import Sequence
from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.notifications.bonus import get_bonus_check_keyboard
from app.services.database.dao.bonus import BonusDAO
from app.services.database.dao.bonus_check import BonusCheckDAO
from app.services.database.models.bonus import Bonus
from app.services.database.models.bonus_check import BonusCheck

from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars
from app.utils.phone import format_phone
from math import ceil


class BonusNotifier(Notifier):
    def __init__(self, bot, session) -> None:
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


class BonusCheckNotifier(Notifier):
    def __init__(self, bot, session) -> None:
        super().__init__(bot, session, MailingType.BONUS_CHECK, BonusCheckDAO(session))
        self._dao: BonusCheckDAO
        self._bonusdao = BonusDAO(session)

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_bonus_checks_to_notify()

    @override
    async def make_notified(self, bonus_check: BonusCheck):
        await self._dao.make_notified(bonus_check)

    async def get_text_parts(self, bonus_check: BonusCheck):
        bonuses = await self.get_bonuses(bonus_check)

        start_date = escape_chars(bonus_check.start_check.strftime("%d.%m.%Y"))
        end_date = escape_chars(bonus_check.end_check.strftime("%d.%m.%Y"))
        text = [f"Бонусы за\n{start_date} \\- {end_date}\n\n"]

        if len(bonuses) == 0:
            text.append("Ни одного бонуса к зачислению")
            return text

        for bonus in bonuses:
            text.append(self.get_text_for_bonus(bonus))

        return text

    async def get_bonuses(self, bonus_check: BonusCheck) -> Sequence[BonusCheck]:
        return await self._bonusdao.get_between_time(
            bonus_check.start_check, bonus_check.end_check
        )

    def get_text_for_bonus(self, bonus: Bonus):
        phone = escape_chars(format_phone(bonus.phone))
        bonus_amount = bonus.bonus_amount
        description = escape_chars(bonus.description)

        return f"*Телефон:* {phone} *Количество:* {bonus_amount}\n*Причина:* {description}\n\n"

    @override
    async def send_notify(self, id: int, bonus_check: BonusCheck) -> None:
        parts = await self.get_text_parts(bonus_check)

        if bonus_check.count_bonuses == 0:
            await self._dao.make_checked(bonus_check)
            await self._bot.send_message(
                chat_id=id,
                text="".join(parts),
            )
            return

        parts_per_message = 15
        messages_count = ceil(len(parts) / parts_per_message)
        for i in range(messages_count - 1):
            start = i * parts_per_message
            end = i * parts_per_message + parts_per_message
            await self._bot.send_message(id, text="".join(parts[start:end]))

        start = (messages_count - 1) * parts_per_message
        await self._bot.send_message(
            id,
            text="".join(parts[start:]),
            reply_markup=get_bonus_check_keyboard(bonus_check.id),
        )
