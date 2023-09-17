from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.consumable_request import ConsumableRequest


class ConsumableRequestNotifyCB(CallbackData, prefix="consumable_request_not"):
    action: Action
    consumable_request_id: int


def get_consumable_request_keyboard(consumable_request: ConsumableRequest):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Сделано",
            callback_data=ConsumableRequestNotifyCB(
                action=Action.SELECT, consumable_request_id=consumable_request.id
            ).pack(),
        )
    )
    return builder.as_markup()


def get_consumable_given_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Выдано ✅", callback_data="completed"))
    return builder.as_markup()
