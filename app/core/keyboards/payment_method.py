from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.manual_start import PaymentMethod


class PaymentMethodTarget(IntEnum):
    CARD = auto()
    CASH = auto()
    NONE = auto()


class PaymentMethodCB(CallbackData, prefix="payment_method"):
    action: Action
    target: PaymentMethodTarget


async def get_payment_method_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    data = await state.get_data()
    payment_method = data.get("payment_method")
    card_status_emoji = "✅" if payment_method == PaymentMethod.CARD else "❌"
    cash_status_emoji = "✅" if payment_method == PaymentMethod.CASH else "❌"

    builder.row(
        types.InlineKeyboardButton(
            text=f"Карта {card_status_emoji}",
            callback_data=PaymentMethodCB(
                action=Action.SELECT, target=PaymentMethodTarget.CARD
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Налчиные {cash_status_emoji}",
            callback_data=PaymentMethodCB(
                action=Action.SELECT, target=PaymentMethodTarget.CASH
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=PaymentMethodCB(
                action=Action.BACK, target=PaymentMethodTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()
