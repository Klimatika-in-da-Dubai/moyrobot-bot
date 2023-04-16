from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class RewashManualStartTarget(IntEnum):
    PHOTO = auto()
    DESCRIPTION = auto()
    NONE = auto()


class RewashManualStartCB(CallbackData, prefix="service_mstart"):
    action: Action
    target: RewashManualStartTarget


def get_rewash_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Фото",
            callback_data=RewashManualStartCB(
                action=Action.ADD_PHOTO, target=RewashManualStartTarget.PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Причина перемывки",
            callback_data=RewashManualStartCB(
                action=Action.ENTER_TEXT, target=RewashManualStartTarget.DESCRIPTION
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=RewashManualStartCB(
                action=Action.BACK, target=RewashManualStartTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=RewashManualStartCB(
                action=Action.ENTER, target=RewashManualStartTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()
