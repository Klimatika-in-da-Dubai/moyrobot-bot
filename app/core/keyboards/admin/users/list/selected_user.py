from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.dao.user import UserDAO
from app.utils.text import escape_chars


class SelectedUserTarget(IntEnum):
    CHANGE = auto()
    DELETE = auto()
    NONE = auto()


class SelectedUserCB(CallbackData, prefix="selected-user"):
    action: Action
    target: SelectedUserTarget


def get_selected_user_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Изменить данные пользователя",
            callback_data=SelectedUserCB(
                action=Action.OPEN, target=SelectedUserTarget.CHANGE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Удалить пользователя",
            callback_data=SelectedUserCB(
                action=Action.SELECT, target=SelectedUserTarget.DELETE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=SelectedUserCB(
                action=Action.BACK, target=SelectedUserTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_selected_user_menu(func, state: FSMContext, session: AsyncSession):
    text = await get_text(state, session)
    await state.set_state(AdminMenu.Users.List.Selected.menu)
    await func(text=text, reply_markup=get_selected_user_keyboard())


async def get_text(state: FSMContext, session: AsyncSession):
    user_id = (await state.get_data()).get("selected_user_id")
    if user_id is None:
        raise ValueError("no user was selected")

    userdao = UserDAO(session=session)
    user = await userdao.get_by_id(id_=user_id)
    if user is None:
        raise Exception("no user with id %s", user_id)

    pincode = await userdao.get_pincode(user_id=user_id)
    if pincode is None:
        pincode = "не сгенерирован"

    return f"Выбранный пользователь: {escape_chars(user.name)}\nПинкод: {pincode}"
