import logging
from typing_extensions import override

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.models.manual_start import (
    ManualStart,
    ManualStartType,
    PaidManualStart,
)
from app.services.database.models.utils import PaymentMethod
from app.services.notifier.manual_start.senders.sender import TypedManualStartSender
from app.services.notifier.utils import get_manual_start_mode_text
from app.utils.text import escape_chars


class PaidManualStartSender(TypedManualStartSender):
    def __init__(self, bot, session):
        super().__init__(bot, session, ManualStartType.PAID)

    def get_text(self, manual_start: ManualStart, typed_manual_start: PaidManualStart):  # type: ignore
        payment_method = PaymentMethod.get_name(typed_manual_start.payment_method)
        return (
            "Получен отчёт о ручном запуске\n"
            "\n"
            "Ручной запуск:\n"
            "*Тип:* Оплата через эквайринг\n"
            f"*ID:* {escape_chars(manual_start.id)}\n"
            f"*Режим:* {escape_chars(get_manual_start_mode_text(manual_start))}\n"
            f"*Тип оплаты:* {payment_method}\n"
            f"*Сумма оплаты:* {typed_manual_start.payment_amount}"
        )

    @override
    async def send(
        self, id: int, manual_start: ManualStart, typed_manual_start: PaidManualStart
    ):
        text = self.get_text(manual_start, typed_manual_start)
        try:
            await self._bot.send_photo(
                id, photo=typed_manual_start.photo_file_id, caption=text
            )
        except Exception:
            logging.error("Can't send report to chat with id %s", id)
