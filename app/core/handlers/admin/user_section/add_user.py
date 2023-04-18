from typing import Any
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import logging
from app.core.filters.admin import isAdminCB

from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action
from app.core.keyboards.admin.users_section.menu import get_users_keyboard


from app.core.keyboards.admin.users_section.add_user import (
    AddUserCB,
    AddUserTarget,
    get_add_user_keyboard,
    get_roles_keyboard,
)
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import Role, User, UserRole

add_user_router = Router()

logger = logging.getLogger("user_add_section")


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.menu,
    AddUserCB.filter((F.target == AddUserTarget.ID) & (F.action == Action.ENTER_TEXT)),
)
async def cb_enter_id(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.UsersSection.Add.id)
    await cb.message.answer("Введите id пользователя")  # type: ignore


@add_user_router.message(AdminMenu.UsersSection.Add.id, F.text)
async def message_user_id(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():  # type: ignore
        await message.answer("Введите число")
        return
    await state.update_data(id=int(message.text))  # type: ignore
    await send_add_user_menu(message, state)


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.menu,
    AddUserCB.filter(
        (F.target == AddUserTarget.NAME) & (F.action == Action.ENTER_TEXT)
    ),
)
async def cb_enter_name(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.UsersSection.Add.name)
    await cb.message.answer("Введите имя пользователя")  # type: ignore


@add_user_router.message(AdminMenu.UsersSection.Add.name, F.text)
async def message_user_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await send_add_user_menu(message, state)


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.menu,
    AddUserCB.filter((F.target == AddUserTarget.ROLES) & (F.action == Action.OPEN)),
)
async def cb_open_role_selection(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminMenu.UsersSection.Add.role)
    await cb.message.edit_text(  # type: ignore
        "Выберете роли пользователя", reply_markup=await get_roles_keyboard(state)
    )


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.role,
    AddUserCB.filter(F.action == Action.SELECT),
)
async def cb_select_role(
    cb: types.CallbackQuery, state: FSMContext, callback_data: AddUserCB
):
    await cb.answer()

    data = await state.get_data()
    if data.get("roles") is None:
        await state.update_data(roles=list())

    roles: list[Role] = (await state.get_data()).get("roles")  # type: ignore
    selected_role = None
    match callback_data.target:
        case AddUserTarget.OPERATOR_ROLE:
            selected_role = Role.OPERATOR
        case AddUserTarget.MODERATOR_ROLE:
            selected_role = Role.MODERATOR
        case AddUserTarget.ADMIN_ROLE:
            selected_role = Role.ADMIN

    if selected_role is None:
        await cb.message.edit_text("Выберете роли пользователя", reply_markup=await get_roles_keyboard(state))  # type: ignore
        return

    if selected_role in roles:
        roles.remove(selected_role)
    else:
        roles.append(selected_role)

    await state.update_data(roles=roles)

    await cb.message.edit_text("Выберете роли пользователя", reply_markup=await get_roles_keyboard(state))  # type: ignore


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.role,
    AddUserCB.filter(F.action == Action.BACK),
)
async def cb_roles_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await edit_text_add_user_menu(cb.message, state)  # type: ignore


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.menu,
    AddUserCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await state.set_state(AdminMenu.UsersSection.menu)
    await cb.message.edit_text("Пользователи", reply_markup=get_users_keyboard())  # type: ignore


@add_user_router.callback_query(
    isAdminCB(),
    AdminMenu.UsersSection.Add.menu,
    AddUserCB.filter(F.action == Action.ENTER),
)
async def cb_enter(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    data = await state.get_data()
    if not is_correct_data(data):
        await cb.answer(text="Не все поля заполнены", show_alert=True)
        return

    logger.info(
        "Admin with id %s, added user with id %s", cb.message.chat.id, data.get("id")  # type: ignore
    )
    user = User(id=data.get("id"), name=data.get("name"))
    user_roles = [UserRole(id=data.get("id"), role=role) for role in data.get("roles")]  # type: ignore
    userdao = UserDAO(session=session)
    await userdao.add_user_with_roles(user, user_roles)

    await cb_back(cb, state)


def is_correct_data(data: dict[str, Any]):
    id = data.get("id")
    name = data.get("name")
    roles = data.get("roles")

    if id is None or id == "":
        return False
    if name is None or name == "":
        return False
    if roles is None or len(roles) == 0:
        return False
    return True


async def send_add_user_menu(message: types.Message, state: FSMContext):
    await state.set_state(AdminMenu.UsersSection.Add.menu)
    await message.answer(
        "Добавить пользователя",
        reply_markup=await get_add_user_keyboard(state),
    )


async def edit_text_add_user_menu(message: types.Message, state: FSMContext):
    await state.set_state(AdminMenu.UsersSection.Add.menu)
    await message.edit_text(
        "Добавить пользователя",
        reply_markup=await get_add_user_keyboard(state),
    )
