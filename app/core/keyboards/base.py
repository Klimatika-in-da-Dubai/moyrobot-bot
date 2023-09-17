from enum import IntEnum, auto

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Action(IntEnum):
    LIST = auto()
    OPEN = auto()
    BACK = auto()
    ENTER = auto()
    ADD = auto()
    DELETE = auto()
    ENTER_TEXT = auto()
    INPUT = auto()
    ADD_PHOTO = auto()
    SELECT = auto()
    CANCEL = auto()


class YesNoTarget(IntEnum):
    YES = auto()
    NO = auto()


class YesNoCB(CallbackData, prefix="yes_no"):
    action: Action
    target: YesNoTarget


def get_yes_no_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Нет",
            callback_data=YesNoCB(action=Action.SELECT, target=YesNoTarget.NO).pack(),
        ),
        types.InlineKeyboardButton(
            text="Да",
            callback_data=YesNoCB(action=Action.SELECT, target=YesNoTarget.YES).pack(),
        ),
    )

    return builder.as_markup()


class CancelCB(CallbackData, prefix="cancel"):
    action: Action


def get_cancel_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Отмена", callback_data=CancelCB(action=Action.CANCEL).pack()
        )
    )
    return builder.as_markup()
