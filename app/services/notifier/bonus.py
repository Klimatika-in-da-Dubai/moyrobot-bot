from collections.abc import Sequence
from datetime import timedelta
from typing_extensions import override

from apscheduler.executors.base import logging
from app.core.keyboards.notifications.bonus import get_approve_bonus_keyboard
from app.services.database.dao.bonus import BonusDAO
from app.services.database.dao.bonus_check import BonusCheckDAO
from app.services.database.models.bonus import Bonus
from app.services.database.models.bonus_check import BonusCheck

from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars
from app.utils.phone import format_phone


class BonusNotifier(Notifier):
    def __init__(self, bot, session, *args) -> None:
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
        self._delta_between_notifies = timedelta(hours=1)

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_bonus_checks_to_notify(self._delta_between_notifies)

    @override
    async def make_notified(self, bonus_check: BonusCheck):
        await self._dao.make_notified(bonus_check)

    async def before(self):
        bonus_checks = await self._dao.get_bonus_checks_to_notify(
            self._delta_between_notifies
        )

        for bonus_check in bonus_checks:
            bonuses = await self.get_bonuses(bonus_check)
            if not bonuses:
                await self._dao.make_checked(bonus_check)
                continue

            for bonus in bonuses:
                for notify in bonus.notify_messages_ids:
                    chat_id, message_id = notify["chat_id"], notify["message_id"]
                    try:
                        await self._bot.delete_message(chat_id, message_id)
                    except Exception as e:
                        logging.error(e)

                await self._bonusdao.delete_notify_messages(bonus)

            for notify in bonus_check.notify_messages_ids:
                chat_id, message_id = notify["chat_id"], notify["message_id"]
                try:
                    await self._bot.delete_message(chat_id, message_id)
                except Exception as e:
                    logging.error(e)

            await self._dao.delete_notify_messages(bonus_check)

    async def send_notify(self, id: int, bonus_check: BonusCheck) -> None:
        if bonus_check.count_bonuses == 0:
            await self._dao.make_checked(bonus_check)
            await self.send_bonus_check_start_message(id, bonus_check)
            return

        bonuses = await self.get_bonuses(bonus_check)

        if not bonuses:
            await self._dao.make_checked(bonus_check)
            return

        await self.send_bonus_check_start_message(id, bonus_check)

        for bonus in bonuses:
            await self.send_bonus_message(id, bonus)

    async def send_bonus_check_start_message(self, id: int, bonus_check: BonusCheck):
        start_date = escape_chars(bonus_check.start_check.strftime("%d.%m.%Y"))
        end_date = escape_chars(bonus_check.end_check.strftime("%d.%m.%Y"))
        text = f"Бонусы за\n{start_date} \\- {end_date}\n\n"
        if bonus_check.count_bonuses == 0:
            text += "Ни одного бонуса к зачислению"
        message = await self._bot.send_message(chat_id=id, text=text)
        await self._dao.add_notify_message_id(bonus_check, id, message.message_id)

    async def send_bonus_message(self, id: int, bonus: Bonus):
        message = await self._bot.send_message(
            id,
            text=self.get_text_for_bonus(bonus),
            reply_markup=get_approve_bonus_keyboard(bonus.id),
        )
        await self._bonusdao.add_notify_message_id(bonus, id, message.message_id)

    async def get_bonuses(self, bonus_check: BonusCheck) -> Sequence[BonusCheck]:
        return await self._bonusdao.get_unhandled_between_time(
            bonus_check.start_check, bonus_check.end_check
        )

    def get_text_for_bonus(self, bonus: Bonus):
        phone = escape_chars(format_phone(bonus.phone))
        bonus_amount = bonus.bonus_amount
        description = escape_chars(bonus.description)

        return f"*Телефон:* {phone}\n*Количество:* {bonus_amount}\n*Причина:* {description}\n\n"
