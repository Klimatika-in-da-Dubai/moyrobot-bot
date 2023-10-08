from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.antifreeze import AntifreezeDAO
from app.services.database.models.antifreeze import Antifreeze

from app.services.database.models.mailing import MailingType
from app.services.database.models.utils import PaymentMethod
from app.services.notifier.base import Notifier


class AntifreezeNotifier(Notifier):
    def __init__(self, bot, session) -> None:
        super().__init__(bot, session, MailingType.ANTIFREEZE, AntifreezeDAO(session))
        self._dao: AntifreezeDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, antifreeze: Antifreeze):
        await self._dao.make_notified(antifreeze)

    def get_text(self, antifreeze: Antifreeze) -> str:
        payment_method = PaymentMethod.get_name(antifreeze.payment_method)
        payment_amount = antifreeze.payment_amount

        return (
            "Продажа незамерзайки\n\n"
            f"*Способ оплаты:* {payment_method}\n"
            f"*Сумма оплаты:* {payment_amount}\n"
        )

    @override
    async def send_notify(self, id: int, antifreeze: Antifreeze) -> None:
        text = self.get_text(antifreeze)
        await self._bot.send_message(id, text=text)
