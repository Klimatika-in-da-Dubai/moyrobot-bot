from enum import IntEnum, auto
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.models.user import Role


class UsersCB(CallbackData, prefix="amenu_user_section"):
    action: Action


def get_users_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Список пользователей",
            callback_data=UsersCB(action=Action.LIST).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Добавить пользователя",
            callback_data=UsersCB(action=Action.ADD).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад", callback_data=UsersCB(action=Action.BACK).pack()
        )
    )
    return builder.as_markup()


async def send_admin_users_menu(func, state: FSMContext):
    await state.set_state(AdminMenu.Users.menu)
    await func(text="Меню пользователи", reply_markup=get_users_keyboard())
