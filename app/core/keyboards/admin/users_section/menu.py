from enum import IntEnum, auto
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action
from app.services.database.models.user import Role


class UsersSectionCB(CallbackData, prefix="amenu_user_section"):
    action: Action


def get_users_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Список пользователей",
            callback_data=UsersSectionCB(action=Action.LIST).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Добавить пользователя",
            callback_data=UsersSectionCB(action=Action.ADD).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Удалить пользователя",
            callback_data=UsersSectionCB(action=Action.DELETE).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад", callback_data=UsersSectionCB(action=Action.BACK).pack()
        )
    )
    return builder.as_markup()
