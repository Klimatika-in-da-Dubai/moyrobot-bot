from collections.abc import Sequence
import datetime
from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.handlers.notifications import promocode
from app.core.keyboards.notifications.promocode import get_promocode_check_keyboard
from app.services.database.dao.promocode import PromocodeDAO
from app.services.database.dao.promocode_check import PromocodeCheckDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.promocode import Promocode
from app.services.database.models.promocode_check import PromocodeCheck
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


class PromocodeCheckNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker) -> None:
        super().__init__(
            bot, session, MailingType.PROMOCODE_CHECK, PromocodeCheckDAO(session)
        )
        self._dao: PromocodeCheckDAO
        self._promocodedao = PromocodeDAO(session)

    @override
    async def get_objects_to_notify(self):
        return await self._dao.get_promocode_checks_to_notify()

    @override
    async def make_notified(self, promocode_check: PromocodeCheck):
        await self._dao.make_notified(promocode_check)

    async def get_text(self, promocode_check: PromocodeCheck):
        promocodes = await self.get_promocodes(promocode_check)

        start_date = escape_chars(promocode_check.start_check.strftime("%d.%m.%Y"))
        end_date = escape_chars(promocode_check.end_check.strftime("%d.%m.%Y"))
        text = f"Промокоды за\n{start_date} \\- {end_date}\n\n"

        if len(promocodes) == 0:
            text += "Ни одного промокода к зачислению"
            return text

        for promocode in promocodes:
            text += self.get_text_for_promocode(promocode)

        return text

    async def get_promocodes(
        self, promocode_check: PromocodeCheck
    ) -> Sequence[Promocode]:
        return await self._promocodedao.get_between_time(
            promocode_check.start_check, promocode_check.end_check
        )

    def get_text_for_promocode(self, promocode: Promocode):
        phone = escape_chars(format_phone(promocode.phone))
        wash_mode = promocode.wash_mode

        return f"*Телефон:* {phone} " f"*Режим:* {wash_mode} "

    @override
    async def send_notify(self, id: int, promocode_check: PromocodeCheck) -> None:
        text = await self.get_text(promocode_check)
        if promocode_check.count_promocodes == 0:
            await self._dao.make_checked(promocode_check)
            await self._bot.send_message(
                chat_id=id,
                text=text,
            )
            return

        await self._bot.send_message(
            id, text=text, reply_markup=get_promocode_check_keyboard(promocode_check.id)
        )
