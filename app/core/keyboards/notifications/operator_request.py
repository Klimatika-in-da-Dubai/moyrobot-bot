from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.operator_request import OperatorRequest


class OperatorRequestNotifyCB(CallbackData, prefix="operator_request_not"):
    action: Action
    operator_request_id: int


def get_operator_request_keyboard(operator_request: OperatorRequest):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Сделано",
            callback_data=OperatorRequestNotifyCB(
                action=Action.SELECT, operator_request_id=operator_request.id
            ).pack(),
        )
    )
    return builder.as_markup()


def get_request_considered_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Рассмотрено ✅", callback_data="completed"))
    return builder.as_markup()
