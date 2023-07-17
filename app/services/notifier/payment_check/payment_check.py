from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.notifications.payment_check import (
    get_card_payment_check_keyboard,
)
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.dao.payment_check import PaymentCheckDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import (
    ManualStart,
    ManualStartType,
)
from app.services.database.models.payment_check import PaymentCheck
from app.services.database.models.utils import PaymentMethod
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class PaymentCheckNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(
            bot, session, MailingType.PAYMENT_CHECK, PaymentCheckDAO(session)
        )
        self._dao: PaymentCheckDAO
        self._manual_start_dao = ManualStartDAO(session)

    async def get_objects_to_notify(self):
        return await self._dao.get_payment_checks_to_notify()

    async def make_notified(self, payment_check: PaymentCheck) -> None:
        await self._dao.make_notified(payment_check)

    async def get_text(self, payment_check: PaymentCheck):
        card_manual_starts = await self.get_card_manual_starts(payment_check)

        date = payment_check.start_check.strftime("%d.%m.%Y")
        text = f"Ручные запуски, оплата через эквайринг картой\nЗа {escape_chars(date)}\n\n"
        if len(list(card_manual_starts)) == 0:
            text += "Ни одной оплаты картой\n"
            return text

        for manual_start in card_manual_starts:
            manual_start_info = await self._manual_start_dao.get_by_id(
                id_=manual_start.id
            )
            if not isinstance(manual_start_info, ManualStart):
                raise TypeError("manual_start error")

            if manual_start_info.mode is None:
                continue

            time = manual_start_info.date.strftime("%H:%M")
            text += f"{time} \\- Терминал: {manual_start_info.terminal_id} \\- Режим: {manual_start_info.mode} \\- Сумма оплаты: {manual_start.payment_amount}\n"

        return text

    async def get_card_manual_starts(
        self, payment_check: PaymentCheck
    ) -> list[ManualStart]:
        manual_starts = await self._manual_start_dao.get_typed_between_time(
            ManualStartType.PAID, payment_check.start_check, payment_check.end_check
        )
        return list(
            filter(lambda x: x.payment_method is PaymentMethod.CARD, manual_starts)
        )

    async def send_notify(self, id: int, payment_check: PaymentCheck):
        text = await self.get_text(payment_check)

        if payment_check.count_manual_starts == 0:
            await self._dao.make_checked(payment_check)
            await self._bot.send_message(
                chat_id=id,
                text=text,
            )
            return

        await self._bot.send_message(
            chat_id=id,
            text=text,
            reply_markup=get_card_payment_check_keyboard(payment_check.id),
        )
