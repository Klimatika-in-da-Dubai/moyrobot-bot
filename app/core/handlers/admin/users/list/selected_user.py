from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.users.list.change import send_change_user_menu
from app.core.keyboards.admin.users.list.menu import send_users_list_menu
from app.core.keyboards.admin.users.list.selected_user import (
    SelectedUserCB,
    SelectedUserTarget,
    send_selected_user_menu,
)
from app.core.keyboards.base import Action, YesNoCB, YesNoTarget, get_yes_no_keyboard

from app.core.states.admin import AdminMenu
from app.services.database.dao.mailing import MailingDAO
from app.services.database.dao.user import UserDAO
from app.utils.list import get_selected_user


selected_user_router = Router()


@selected_user_router.callback_query(
    AdminMenu.Users.List.Selected.menu,
    isAdminCB(),
    SelectedUserCB.filter(
        (F.action == Action.SELECT) & (F.target == SelectedUserTarget.DELETE)
    ),
)
async def cb_delete(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    user = await get_selected_user(state, session)
    if user is None:
        await cb.message.edit_text("Такого пользователя нет в базе данных")  # type: ignore
        await send_users_list_menu(cb.message.edit_text, state, session)  # type: ignore
        return
    await state.set_state(AdminMenu.Users.List.Selected.delete)
    await cb.message.edit_text(  # type: ignore
        f"Вы точно хотите удалить пользователя: {user.name}",
        reply_markup=get_yes_no_keyboard(),
    )


@selected_user_router.callback_query(
    AdminMenu.Users.List.Selected.menu,
    isAdminCB(),
    SelectedUserCB.filter(
        (F.action == Action.OPEN) & (F.target == SelectedUserTarget.CHANGE)
    ),
)
async def cb_change(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    user = await get_selected_user(state, session)
    if user is None:
        await cb.answer("Пользователя нет в базе данных", show_alert=True)
        await send_users_list_menu(cb.message.edit_text, state, session)  # type: ignore
        return

    await cb.answer()
    userdao = UserDAO(session)
    mailingdao = MailingDAO(session)
    await state.update_data(id=user.id)
    await state.update_data(name=user.name)
    await state.update_data(roles=await userdao.get_user_roles(user))
    await state.update_data(salary=await userdao.get_salary(user))
    await state.update_data(mailings=await mailingdao.get_user_mailings(user))

    await send_change_user_menu(cb.message.edit_text, state)  # type: ignore


@selected_user_router.callback_query(
    AdminMenu.Users.List.Selected.delete,
    isAdminCB(),
    YesNoCB.filter(F.target == YesNoTarget.YES),
)
async def cb_delete_yes(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    userdao = UserDAO(session)
    user = await get_selected_user(state, session)
    await userdao.delete_user(user)
    await send_users_list_menu(cb.message.edit_text, state, session)  # type: ignore


@selected_user_router.callback_query(
    AdminMenu.Users.List.Selected.delete,
    isAdminCB(),
    YesNoCB.filter(F.target == YesNoTarget.NO),
)
async def cb_delete_no(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_selected_user_menu(cb.message.edit_text, state, session)  # type: ignore


@selected_user_router.callback_query(
    AdminMenu.Users.List.Selected.menu,
    isAdminCB(),
    SelectedUserCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(selected_user=None)
    await send_users_list_menu(cb.message.edit_text, state, session)  # type: ignore
