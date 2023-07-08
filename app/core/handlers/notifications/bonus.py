from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.notifications.bonus import (
    BonusNotificationCB,
    BonusNotificationTarget,
    get_approve_keyboard,
    get_remind_keyboard,
)


card_payment_router = Router()


@card_payment_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.APPROVE) & (F.action == Action.SELECT)
    )
)
async def cb_approve_card_payment_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()
    # Code for approving
    # ...

    await cb.message.edit_reply_markup(reply_markup=get_approve_keyboard())  # type: ignore


@card_payment_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.REMIND) & (F.action == Action.SELECT)
    )
)
async def cb_remind_card_payment_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: async_sessionmaker,
):
    cb.answer()

    # Code for remind
    # ...

    await cb.message.edit_reply_markup(reply_markup=get_remind_keyboard())  # type: ignore
