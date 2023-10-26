from datetime import datetime, time
from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.services.checker.shift.cashbox.checker import CashboxChecker
from app.services.checker.shift.shift import ShiftChecker
from app.services.database.dao.mailing import get_mailing_ids

from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO, ShiftDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.shift import CloseShift, Shift


async def auto_close_shift(bot: Bot, sessionmaker: async_sessionmaker, *args) -> None:
    async with sessionmaker() as session:
        shiftdao = ShiftDAO(session=session)
        shift = await shiftdao.get_last_shift()

        if not shift.is_should_be_closed():
            return

        if (
            shift.is_daily_shift()
            and datetime.now().time() < time.fromisoformat("22:30")
        ) or (
            shift.is_nightly_shift()
            and datetime.now().time() < time.fromisoformat("10:30")
        ):
            return

        shift.close_date = datetime.now()
        shift.closed_by_id = shift.opened_by_id
        shift.closed_automaticaly = True

        await shiftdao.add_shift(shift)

        await add_close_shift(shift, session)

        await ShiftChecker(session).check(shift)
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


async def add_close_shift(shift: Shift, session: AsyncSession) -> None:
    closeshiftdao = CloseShiftDAO(session)
    close_shift = await create_close_shift_from_shift(shift, session)
    await closeshiftdao.add_shift(close_shift)


async def create_close_shift_from_shift(
    shift: Shift, session: AsyncSession
) -> CloseShift:
    openshiftdao = OpenShiftDAO(session)
    openshift = await openshiftdao.get_by_id(shift.id)
    if openshift is None:
        raise ValueError()

    closeshift = CloseShift(id=shift.id, date=shift.close_date)
    closeshift.money_amount = openshift.money_amount + await CashboxChecker(
        session
    ).get_cashbox_diff(shift)

    closeshift.antifreeze_count = openshift.antifreeze_count
    closeshift.shampoo_count = openshift.shampoo_count
    closeshift.foam_count = openshift.foam_count
    closeshift.wax_count = openshift.wax_count
    closeshift.shampoo_check = openshift.shampoo_check
    closeshift.foam_check = openshift.foam_check
    closeshift.wax_check = openshift.wax_check
    closeshift.napkins_check = openshift.napkins_check
    closeshift.coins_check = openshift.coins_check
    closeshift.equipment_check = openshift.equipment_check
    closeshift.robot_movement_check = openshift.robot_movement_check
    closeshift.robot_leak_check = openshift.robot_leak_check
    closeshift.gates_check = openshift.gates_check
    return closeshift
