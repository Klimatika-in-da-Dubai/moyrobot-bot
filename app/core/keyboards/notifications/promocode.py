from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class PromocodeNotificationTarget(IntEnum):
    APPROVE = auto()
    REMIND = auto()


class PromocodeNotificationCB(CallbackData, prefix="promocode_check"):
    action: Action
    target: PromocodeNotificationTarget
    id: int


def get_promocode_check_keyboard(id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Напомнить ❌",
            callback_data=PromocodeNotificationCB(
                action=Action.SELECT, target=PromocodeNotificationTarget.REMIND, id=id
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Начислено ✅",
            callback_data=PromocodeNotificationCB(
                action=Action.SELECT, target=PromocodeNotificationTarget.APPROVE, id=id
            ).pack(),
        ),
    )
    return builder.as_markup()


def get_approve_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Начислено ✅", callback_data="NothingSpecial")
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
