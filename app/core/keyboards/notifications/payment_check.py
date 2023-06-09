from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class CardPaymentCheckTarget(IntEnum):
    APPROVE = auto()
    REMIND = auto()


class CardPaymentCheckCB(CallbackData, prefix="card_payment_check"):
    action: Action
    target: CardPaymentCheckTarget
    id: int


def get_card_payment_check_keyboard(id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Напомнить ❌",
            callback_data=CardPaymentCheckCB(
                action=Action.SELECT, target=CardPaymentCheckTarget.REMIND, id=id
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Подтвердить ✅",
            callback_data=CardPaymentCheckCB(
                action=Action.SELECT, target=CardPaymentCheckTarget.APPROVE, id=id
            ).pack(),
        ),
    )
    return builder.as_markup()


def get_approve_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Подтверждено ✅", callback_data="NothingSpecial"
        )
    )
    return builder.as_markup()


def get_remind_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Напомним через час ❌", callback_data="NothingSpecial"
        )
    )
    return builder.as_markup()
