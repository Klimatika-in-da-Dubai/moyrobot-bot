from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.money_collection import MoneyCollectionDAO
from app.services.database.dao.shift import ShiftDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.money_collection import MoneyCollection
from app.services.database.models.shift import Shift
from app.services.notifier.base import Notifier


class MoneyCollectionNotifier(Notifier):
    def __init__(
        self,
        bot: Bot,
        session: AsyncSession,
    ):
        super().__init__(
            bot, session, MailingType.MONEY_COLLECTION, MoneyCollectionDAO(session)
        )
        self._dao: MoneyCollectionDAO
        self._shiftdao = ShiftDAO(session)

    async def get_objects_to_notify(self):
        shift: Shift = await self._shiftdao.get_last_closed()
        return await self._dao.get_unnotified_between_time(
            shift.open_date, shift.close_date
        )

    async def make_notified(self, money_collection: MoneyCollection) -> None:
        await self._dao.make_notified(money_collection)

    def get_text(self, money_collection: MoneyCollection):
        text = "Была произведена инкассация\n"
        text += f"*Сумма инкассации:* {money_collection.money_amount}"
        return text

    async def send_notify(
        self, id: int, money_collection: MoneyCollection, debug: bool = False
    ):
        text = self.get_text(money_collection)
        await self._bot.send_message(id, text=text)
