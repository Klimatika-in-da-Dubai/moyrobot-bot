from typing import Iterable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import User


class UsersListCB(CallbackData, prefix="user-list"):
    action: Action
    user_id: int


async def get_users_list_keyboard(users: Iterable[User]) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.row(
            types.InlineKeyboardButton(
                text=f"{user.name}",
                callback_data=UsersListCB(action=Action.OPEN, user_id=user.id).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=UsersListCB(action=Action.BACK, user_id=-1).pack(),
        )
    )
    return builder.as_markup()


async def send_users_list_menu(func, state: FSMContext, session: async_sessionmaker):
    userdao = UserDAO(session=session)
    users = await userdao.get_all_active()
    await state.set_state(AdminMenu.Users.List.menu)
    await func(
        text="Выберите пользователя", reply_markup=await get_users_list_keyboard(users)
    )
