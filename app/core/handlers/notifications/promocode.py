from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.notifications.promocode import (
    PromocodeNotificationCB,
    PromocodeNotificationTarget,
    get_approve_keyboard,
    get_remind_keyboard,
)
from app.services.database.dao.promocode_check import PromocodeCheckDAO
from app.services.database.models.promocode_check import PromocodeCheck


promocode_router = Router()


@promocode_router.callback_query(
    PromocodeNotificationCB.filter(
        (F.target == PromocodeNotificationTarget.APPROVE) & (F.action == Action.SELECT)
    )
)
async def cb_approve_promocode_check(
    cb: types.CallbackQuery,
    callback_data: PromocodeNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()

    promocode_check_dao = PromocodeCheckDAO(session)
    promocode_check = await promocode_check_dao.get_by_id(callback_data.id)
    if not isinstance(promocode_check, PromocodeCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await promocode_check_dao.make_checked(promocode_check)
    await cb.message.edit_reply_markup(reply_markup=get_approve_keyboard())  # type: ignore


@promocode_router.callback_query(
    PromocodeNotificationCB.filter(
        (F.target == PromocodeNotificationTarget.REMIND) & (F.action == Action.SELECT)
    )
)
async def cb_remind_promocode_check(
    cb: types.CallbackQuery,
    callback_data: PromocodeNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()

    promocode_check_dao = PromocodeCheckDAO(session)
    promocode_check = await promocode_check_dao.get_by_id(callback_data.id)
    if not isinstance(promocode_check, PromocodeCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await cb.message.edit_reply_markup(reply_markup=get_remind_keyboard())  # type: ignore
