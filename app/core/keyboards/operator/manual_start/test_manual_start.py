from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class TestManualStartTarget(IntEnum):
    NONE = auto()
    DESCRIPTION = auto()


class TestManualStartCB(CallbackData, prefix="test_mstart"):
    action: Action
    target: TestManualStartTarget


def get_test_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Причина запуска",
            callback_data=TestManualStartCB(
                action=Action.ENTER_TEXT, target=TestManualStartTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=TestManualStartCB(
                action=Action.BACK, target=TestManualStartTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=TestManualStartCB(
                action=Action.ENTER, target=TestManualStartTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()
