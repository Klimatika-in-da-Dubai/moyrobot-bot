from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.payment_check import PaymentCheckDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.payment_check import PaymentCheck
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class PaymentCheckAlertNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(
            bot, session, MailingType.PAYMENT_CHECK_ALERT, PaymentCheckDAO(session)
        )
        self._dao: PaymentCheckDAO

    async def get_objects_to_notify(self):
        return await self._dao.get_payment_checks_to_alert()

    async def make_notified(self, payment_check: PaymentCheck) -> None:
        await self._dao.make_alerted(payment_check)

    def get_text(self, payment_check: PaymentCheck) -> str:
        start_date = escape_chars(payment_check.start_check.strftime("%d.%m.%Y"))
        end_date = escape_chars(payment_check.end_check.strftime("%d.%m.%Y"))
        text = "Не было проверки ручных запусков с оплатой через эквайринг\n"
        text += f"В периоде за {start_date} \\- {end_date}\n"
        return text

    async def send_notify(self, id: int, payment_check: PaymentCheck) -> None:
        text = self.get_text(payment_check)
        await self._bot.send_message(id, text=text)
