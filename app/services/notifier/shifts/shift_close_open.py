from dataclasses import dataclass
from typing_extensions import override
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.checker.shift.cashbox.outcome.object.money_collection import (
    MoneyCollectionOutcome,
)
from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO, ShiftDAO
from app.services.database.dao.shift_check import ShiftCheckDAO
from app.services.database.dao.shifts_difference import ShiftsDifferenceDAO
from app.services.database.dao.user import UserDAO

from app.services.database.models.mailing import MailingType
from app.services.database.models.shift import CloseShift, OpenShift, Shift
from app.services.notifier.base import Notifier
from app.services.notifier.cleaning import CleaningNotifier
from app.utils.text import escape_chars


@dataclass
class CloseOpenShiftInfo:
    closed_shift: Shift
    opened_shift: Shift


class CloseOpenShiftNotifier(Notifier):
    def __init__(
        self,
        bot: Bot,
        session: async_sessionmaker,
    ) -> None:
        after_notifiers = [CleaningNotifier(bot, session)]
        super().__init__(
            bot,
            session,
            MailingType.SHIFT,
            ShiftDAO(session),
            after_notifiers=after_notifiers,
        )
        self._dao: ShiftDAO
        self._userdao = UserDAO(session)
        self._closeshiftdao = CloseShiftDAO(session)
        self._openshiftdao = OpenShiftDAO(session)
        self._shiftcheckdao = ShiftCheckDAO(session)
        self._shiftdifferencedao = ShiftsDifferenceDAO(session)
        self._moneycollectiongetter = MoneyCollectionOutcome(session)

    @override
    async def get_objects_to_notify(self):
        if not await self._dao.is_shift_opened():
            return []

        closed_shift = await self._dao.get_last_closed()
        opened_shift = await self._dao.get_last_shift()

        if opened_shift is None:
            return []

        if closed_shift.notified is True and opened_shift.notified is True:
            return []

        return [
            CloseOpenShiftInfo(
                closed_shift=closed_shift,
                opened_shift=opened_shift,
            )
        ]

    @override
    async def make_notified(self, info: CloseOpenShiftInfo):
        await self._dao.make_notified(info.closed_shift)
        await self._dao.make_notified(info.opened_shift)

    async def get_text(self, info: CloseOpenShiftInfo) -> str:
        close_shift_text = await self.get_close_shift_text(info.closed_shift)
        open_shift_text = await self.get_open_shift_text(info.opened_shift)
        money_check_text = await self.get_money_check_text(info)
        return f"{close_shift_text}\n{open_shift_text}\n{money_check_text}\n"

    async def get_close_shift_text(self, shift: Shift) -> str:
        close_shift = await self._closeshiftdao.get_by_id(shift.id)

        if not isinstance(close_shift, CloseShift):
            raise ValueError("close shift is None")

        return "*Закрытие*\n" + (await self.get_shift_text(shift, close_shift))

    async def get_open_shift_text(self, shift: Shift) -> str:
        open_shift = await self._openshiftdao.get_by_id(shift.id)

        if not isinstance(open_shift, OpenShift):
            raise ValueError("open shift is None")

        return "*Открытие*\n" + (await self.get_shift_text(shift, open_shift))

    async def get_shift_text(
        self, shift: Shift, shift_info: CloseShift | OpenShift
    ) -> str:
        names = [await self._userdao.get_user_name_by_id(shift.opened_by_id)]
        if shift.closed_by_id is not None and shift.opened_by_id != shift.closed_by_id:
            names.append(await self._userdao.get_user_name_by_id(shift.closed_by_id))

        names_text = escape_chars(", ".join(names))
        money_text = shift_info.money_amount
        chemistry_text = shift_info.chemistry_count

        antifreeze_sentence = ""
        if shift_info.antifreeze_count != 0:
            antifreeze_sentence = f"Антифриз: {shift_info.antifreeze_count}\n"

        return (
            f"ФИО: {names_text}\n"
            f"Деньги: {money_text} ₽\n"
            f"Количество химии: {chemistry_text}\n" + antifreeze_sentence
        )

    async def get_money_check_text(self, info: CloseOpenShiftInfo) -> str:
        shift_open = await self._openshiftdao.get_by_id(info.opened_shift.id)
        shift_check = await self._shiftcheckdao.get_by_id(info.closed_shift.id)
        money_difference = await self._shiftdifferencedao.get_by_ids(
            info.closed_shift.id, info.opened_shift.id
        )
        money_collection = await self._moneycollectiongetter.get_outcome(
            info.closed_shift
        )
        if not all([shift_open, shift_check, money_difference]):
            raise ValueError("Some data is None")

        shift_money_difference = (
            0 if shift_check.money_difference > 0 else shift_check.money_difference
        )
        return (
            "*Проверка денег*\n"
            f"Недостача за закрытую смену: "
            f"{escape_chars(str(shift_money_difference))} ₽\n"  # type: ignore
            f"Инкассация: {escape_chars(str(money_collection))} ₽\n"
            f"Итого в кассе: {escape_chars(str(shift_open.money_amount))} ₽\n"  # type: ignore
            f"Разница между сменами : {escape_chars(str(money_difference.money_difference))} ₽\n"
        )

    @override
    async def send_notify(self, id: int, info: CloseOpenShiftInfo) -> None:
        text = await self.get_text(info)
        await self._bot.send_message(id, text)

    @override
    async def before_notify(self):
        return await super().before_notify()
