import datetime
from datetime import time
from enum import IntEnum, auto
from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.shift import ShiftDAO
from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier


class ShiftNotifyType(IntEnum):
    SHIFT_NOT_OPENED = auto()
    SHIFT_NOT_CLOSED = auto()


class ShiftNotifyNotifier(Notifier):
    def __init__(self, bot, session) -> None:
        super().__init__(bot, session, MailingType.SHIFT_NOTIFY, ShiftDAO(session))
        self._dao: ShiftDAO

    async def get_objects_to_notify(self) -> list:
        shift = await self._dao.get_last_shift()
        if shift.is_should_be_closed():
            return [ShiftNotifyType.SHIFT_NOT_CLOSED]

        if (
            time.fromisoformat("09:30")
            < datetime.datetime.now().time()
            < time.fromisoformat("20:30")
            or (
                time.fromisoformat("21:30") < datetime.datetime.now().time()
                or datetime.datetime.now().time() < time.fromisoformat("08:30")
            )
        ) and not (await self._dao.is_shift_opened()):
            return [ShiftNotifyType.SHIFT_NOT_OPENED]

        return []

    async def make_notified(self, obj) -> None:
        pass

    def get_text(self, notify_type: ShiftNotifyType) -> str:
        match notify_type:
            case ShiftNotifyType.SHIFT_NOT_OPENED:
                return "ВНИМАНИЕ! Смена не открыта. Пожалуйста, откройте смену"
            case ShiftNotifyType.SHIFT_NOT_CLOSED:
                return "ВНИМАНИЕ! Смена не закрыта. Пожалуйста, закройте смену"

    async def send_notify(self, id: int, notify_type: ShiftNotifyType) -> None:
        text = self.get_text(notify_type)
        await self._bot.send_message(id, text, parse_mode=ParseMode.HTML)
