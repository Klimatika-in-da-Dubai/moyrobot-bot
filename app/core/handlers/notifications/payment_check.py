from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.notifications.payment_check import (
    CardPaymentCheckCB,
    CardPaymentCheckTarget,
    get_approve_keyboard,
    get_remind_keyboard,
)
from app.services.database.dao.payment_check import PaymentCheckDAO
from app.services.database.models.payment_check import PaymentCheck


card_payment_router = Router()


@card_payment_router.callback_query(
    CardPaymentCheckCB.filter(
        (F.target == CardPaymentCheckTarget.APPROVE) & (F.action == Action.SELECT)
    )
)
async def cb_approve_card_payment_check(
    cb: types.CallbackQuery,
    callback_data: CardPaymentCheckCB,
    session: async_sessionmaker,
):
    cb.answer()

    payment_check_dao = PaymentCheckDAO(session)
    payment_check = await payment_check_dao.get_by_id(callback_data.id)
    if not isinstance(payment_check, PaymentCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await payment_check_dao.make_checked(payment_check)
    await cb.message.edit_reply_markup(reply_markup=get_approve_keyboard())  # type: ignore


@card_payment_router.callback_query(
    CardPaymentCheckCB.filter(
        (F.target == CardPaymentCheckTarget.REMIND) & (F.action == Action.SELECT)
    )
)
async def cb_remind_card_payment_check(
    cb: types.CallbackQuery,
    callback_data: CardPaymentCheckCB,
    session: async_sessionmaker,
):
    cb.answer()

    payment_check_dao = PaymentCheckDAO(session)
    payment_check = await payment_check_dao.get_by_id(callback_data.id)
    if not isinstance(payment_check, PaymentCheck):
        await cb.message.edit_text("Произошла ошибка в базе данных")  # type: ignore

    await cb.message.edit_reply_markup(reply_markup=get_remind_keyboard())  # type: ignore
