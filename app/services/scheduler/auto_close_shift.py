from datetime import datetime, time
from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.checker.shift.cashbox.checker import CashboxChecker
from app.services.database.dao.mailing import get_mailing_ids

from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO, ShiftDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.shift import CloseShift, Shift


async def auto_close_shift(bot: Bot, session: async_sessionmaker) -> None:
    shiftdao = ShiftDAO(session=session)
    shift = await shiftdao.get_last_shift()

    if not shift.is_should_be_closed():
        return

    if (
        shift.is_daily_shift() and datetime.now().time() < time.fromisoformat("22:30")
    ) or (
        shift.is_nightly_shift() and datetime.now().time() < time.fromisoformat("10:30")
    ):
        return

    shift.close_date = datetime.now()
    shift.closed_by_id = shift.opened_by_id
    shift.closed_automaticaly = True

    await shiftdao.add_shift(shift)

    await add_close_shift(shift, session)

    mailings_id = await get_mailing_ids(session, MailingType.SHIFT_NOTIFY)
    for id in mailings_id:
        try:
            await bot.send_message(
                id,
                "ВНИМАНИЕ! Смена была автоматически закрыта!\n",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


async def add_close_shift(shift: Shift, session: async_sessionmaker) -> None:
    closeshiftdao = CloseShiftDAO(session)
    close_shift = await get_close_shift(shift, session)
    await closeshiftdao.add_shift(close_shift)


async def get_close_shift(shift: Shift, session: async_sessionmaker) -> CloseShift:
    openshiftdao = OpenShiftDAO(session)
    openshift = await openshiftdao.get_by_id(shift.id)
    if openshift is None:
        raise ValueError()

    closeshift = CloseShift(id=shift.id, date=shift.close_date)
    closeshift.money_amount = openshift.money_amount + await CashboxChecker(
        session
    ).get_cashbox_diff(shift)

    closeshift.antifreeze_count = openshift.antifreeze_count
    closeshift.chemistry_count = closeshift.chemistry_count
    closeshift.chemistry_check = closeshift.chemistry_check
    closeshift.equipment_check = closeshift.equipment_check
    closeshift.robot_movement_check = closeshift.robot_movement_check
    closeshift.robot_leak_check = closeshift.robot_leak_check
    closeshift.gates_check = closeshift.gates_check
    return closeshift
