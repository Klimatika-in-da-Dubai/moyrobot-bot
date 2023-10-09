from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class BonusNotificationTarget(IntEnum):
    APPROVE = auto()
    DECLINE = auto()


class BonusNotificationCB(CallbackData, prefix="bonus_check"):
    action: Action
    target: BonusNotificationTarget
    id: int


def get_approve_bonus_keyboard(id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Отклонить ❌",
            callback_data=BonusNotificationCB(
                action=Action.SELECT, target=BonusNotificationTarget.DECLINE, id=id
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Начислить ✅",
            callback_data=BonusNotificationCB(
                action=Action.SELECT, target=BonusNotificationTarget.APPROVE, id=id
            ).pack(),
        ),
    )
    return builder.as_markup()


def get_approve_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Начислено ✅", callback_data="NothingSpecial")
    )
    return builder.as_markup()


def get_no_client_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Нет такого клиента ⚠️", callback_data="NothingSpecial"
        )
    )
    return builder.as_markup()


def get_decline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Отклонено ❌", callback_data="NothingSpecial")
    )
    return builder.as_markup()
