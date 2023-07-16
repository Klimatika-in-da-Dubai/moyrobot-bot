from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.notifications.bonus import (
    BonusNotificationCB,
    BonusNotificationTarget,
    get_approve_keyboard,
    get_remind_keyboard,
)
from app.services.database.dao.bonus_check import BonusCheckDAO
from app.services.database.models.bonus_check import BonusCheck


bonus_router = Router()


@bonus_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.APPROVE) & (F.action == Action.SELECT)
    )
)
async def cb_approve_bonus_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()

    bonus_check_dao = BonusCheckDAO(session)
    bonus_check = await bonus_check_dao.get_by_id(callback_data.id)
    if not isinstance(bonus_check, BonusCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await bonus_check_dao.make_checked(bonus_check)
    await cb.message.edit_reply_markup(reply_markup=get_approve_keyboard())  # type: ignore


@bonus_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.REMIND) & (F.action == Action.SELECT)
    )
)
async def cb_remind_bonus_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()

    bonus_check_dao = BonusCheckDAO(session)
    bonus_check = await bonus_check_dao.get_by_id(callback_data.id)
    if not isinstance(bonus_check, BonusCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await cb.message.edit_reply_markup(reply_markup=get_remind_keyboard())  # type: ignore
