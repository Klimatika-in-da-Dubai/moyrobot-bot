from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.users.list.menu import UsersListCB
from app.core.keyboards.admin.users.list.selected_user import send_selected_user_menu
from app.core.keyboards.admin.users.menu import send_admin_users_menu
from app.core.keyboards.base import Action

from app.core.states.admin import AdminMenu


menu_router = Router()


@menu_router.callback_query(
    AdminMenu.Users.List.menu,
    isAdminCB(),
    UsersListCB.filter((F.action == Action.OPEN)),
)
async def cb_open_user(
    cb: types.CallbackQuery,
    callback_data: UsersListCB,
    state: FSMContext,
    session: AsyncSession,
):
    await cb.answer()
    await state.update_data(selected_user_id=callback_data.user_id)
    await send_selected_user_menu(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    AdminMenu.Users.List.menu,
    isAdminCB(),
    UsersListCB.filter((F.action == Action.BACK)),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_admin_users_menu(cb.message.edit_text, state)  # type: ignore
