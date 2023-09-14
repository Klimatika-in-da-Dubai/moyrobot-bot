from datetime import timedelta
from typing import assert_never
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.notifications.consumable_request import (
    get_consumable_request_keyboard,
)
from app.services.database.dao.consumable_request import ConsumableRequestDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.consumable_request import (
    Consumable,
    ConsumableRequest,
)
from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class ConsumableRequestNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(
            bot, session, MailingType.OPERATOR_REQUEST, ConsumableRequestDAO(session)
        )
        self._dao: ConsumableRequestDAO
        self._userdao = UserDAO(session)

    async def get_objects_to_notify(self):
        delta_between_notifies = timedelta(hours=1)
        return await self._dao.get_requests_to_notify(delta_between_notifies)

    async def make_notified(self, consumable_request: ConsumableRequest) -> None:
        await self._dao.make_notified(consumable_request)

    async def send_notify(
        self, id: int, consumable_request: ConsumableRequest, debug: bool = False
    ):
        text = await self.get_text(consumable_request)

        message = await self._bot.send_message(
            id,
            text=text,
            reply_markup=get_consumable_request_keyboard(consumable_request),
        )
        await self._dao.add_notify_message_id(
            consumable_request, id, message.message_id
        )
        await self._dao.make_notified(consumable_request)

    async def get_text(self, consumable_request: ConsumableRequest) -> str:
        match consumable_request.consumable:
            case Consumable.SHAMPOO:
                consumable = "шампунь"
            case Consumable.FOAM:
                consumable = "пену"
            case Consumable.WAX:
                consumable = "воск"
            case Consumable.COINS:
                consumable = "монетки"
            case Consumable.NAPKINS:
                consumable = "салфетки"
            case _ as never:
                assert_never(never)

        return escape_chars(f"⚠️ Необходимо выдать {consumable}!")
