from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class ServiceManualStartTarget(IntEnum):
    DESCRIPTION = auto()
    NONE = auto()


class ServiceManualStartCB(CallbackData, prefix="service_mstart"):
    action: Action
    target: ServiceManualStartTarget


def get_service_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Причина",
            callback_data=ServiceManualStartCB(
                action=Action.ENTER_TEXT,
                target=ServiceManualStartTarget.DESCRIPTION,
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ServiceManualStartCB(
                action=Action.BACK,
                target=ServiceManualStartTarget.NONE,
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=ServiceManualStartCB(
                action=Action.ENTER, target=ServiceManualStartTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()
