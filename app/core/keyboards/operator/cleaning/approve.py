from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


class CleaningApproveTarget(IntEnum):
    DECLINE = auto()
    APPROVE = auto()


class CleaningApproveCB(CallbackData, prefix="cleaning_approve"):
    action: Action
    target: CleaningApproveTarget
    cleaning_id: int


def get_cleaning_approve_keyboard(cleaning_id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Отклонить ❌",
            callback_data=CleaningApproveCB(
                action=Action.SELECT,
                target=CleaningApproveTarget.DECLINE,
                cleaning_id=cleaning_id,
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Принять ✅",
            callback_data=CleaningApproveCB(
                action=Action.SELECT,
                target=CleaningApproveTarget.APPROVE,
                cleaning_id=cleaning_id,
            ).pack(),
        ),
    )
    return builder.as_markup()
