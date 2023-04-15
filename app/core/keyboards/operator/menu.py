from enum import IntEnum, auto
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action


class OperatorMenuTarget(IntEnum):
    NONE = auto()
    MANUAL_START = auto()


class OperatorMenuCB(CallbackData, prefix="operator_menu"):
    action: Action
    target: OperatorMenuTarget


def get_operator_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Ручной запуск",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=OperatorMenuCB(
                action=Action.BACK, target=OperatorMenuTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()
