from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import Role


class MenuTarget(IntEnum):
    OPERATOR_MENU = auto()
    MODERATOR_MENU = auto()
    ADMIN_MENU = auto()
    FEEDBACK_MENU = auto()


class MenuCB(CallbackData, prefix="menu"):
    action: Action
    target: MenuTarget


async def get_menu_keyboard(
    chat_id: int, session: async_sessionmaker
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    userdao = UserDAO(session=session)
    user = await userdao.get_by_id(chat_id)
    user_roles = await userdao.get_user_roles(user)  # type: ignore

    if any(
        role in user_roles for role in (Role.OPERATOR, Role.ADMIN, Role.WORK_ACCOUNT)
    ):
        builder.row(
            types.InlineKeyboardButton(
                text="Меню оператора",
                callback_data=MenuCB(
                    action=Action.OPEN, target=MenuTarget.OPERATOR_MENU
                ).pack(),
            )
        )

    if any(role in user_roles for role in (Role.MODERATOR, Role.ADMIN)):
        builder.row(
            types.InlineKeyboardButton(
                text="Меню модератора",
                callback_data=MenuCB(
                    action=Action.OPEN, target=MenuTarget.MODERATOR_MENU
                ).pack(),
            )
        )

    if Role.ADMIN in user_roles:
        builder.row(
            types.InlineKeyboardButton(
                text="Меню админа",
                callback_data=MenuCB(
                    action=Action.OPEN, target=MenuTarget.ADMIN_MENU
                ).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Связь с администрацией",
            callback_data=MenuCB(
                action=Action.OPEN, target=MenuTarget.FEEDBACK_MENU
            ).pack(),
        )
    )

    return builder.as_markup()


async def send_menu_keyboard(
    send_func: Callable,
    message: types.Message,
    state: FSMContext,
    session: async_sessionmaker,
) -> None:
    await state.clear()

    await send_func(
        text="Меню", reply_markup=await get_menu_keyboard(message.chat.id, session)
    )
