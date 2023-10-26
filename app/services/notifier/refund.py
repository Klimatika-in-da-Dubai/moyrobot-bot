from typing_extensions import override
from aiogram.types import InputMediaPhoto
from app.services.database.dao.refund import RefundDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.refund import PaymentDevice, Refund
from app.services.database.models.utils import PaymentMethod
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class RefundNotifier(Notifier):
    def __init__(self, bot, session, *args) -> None:
        super().__init__(bot, session, MailingType.REFUND, RefundDAO(session))
        self._dao: RefundDAO

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    @override
    async def make_notified(self, refund: Refund):
        await self._dao.make_notified(refund)

    def get_caption(self, refund: Refund):
        payment_device = PaymentDevice.get_name(refund.payment_device)
        payment_method = PaymentMethod.get_name(refund.payment_method)
        description = escape_chars(refund.description)

        return (
            f"Возврат\n\n"
            f"*Оплата через:* {payment_device}\n"
            f"*Способ оплаты:* {payment_method}\n"
            f"*Причина:* {description}\n"
        )

    def get_media_group(self, refund: Refund):
        caption = self.get_caption(refund)
        media = []
        media.append(
            InputMediaPhoto(  # type: ignore
                media=refund.statement_photo_file_id, caption=caption
            )
        )
        if not (
            refund.payment_device == PaymentDevice.TERMINAL
            and refund.payment_method == PaymentMethod.CARD
        ):
            media.append(InputMediaPhoto(media=refund.consumable_photo_file_id))  # type: ignore
        return media

    @override
    async def send_notify(self, id: int, refund: Refund) -> None:
        media = self.get_media_group(refund)
        await self._bot.send_media_group(id, media)
