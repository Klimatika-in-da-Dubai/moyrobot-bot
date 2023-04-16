from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class ManualStartReportTarget(IntEnum):
    TEST_MANUAL_START = auto()
    SERVICE_MANUAL_START = auto()
    REWASH_MANUAL_START = auto()
    PAID_MANUAL_START = auto()
    NONE = auto()


class ManualStartReportCB(CallbackData, prefix="mstart_report"):
    action: Action
    target: ManualStartReportTarget


def get_manual_start_type_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Тест",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.TEST_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Технический",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.SERVICE_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Перемывка",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.REWASH_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Оплата через эквайринг",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.PAID_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ManualStartReportCB(
                action=Action.BACK, target=ManualStartReportTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()
