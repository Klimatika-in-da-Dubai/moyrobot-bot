import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.menu import (
    AdminMenuCB,
    AdminMenuTarget,
)
from app.core.keyboards.admin.users.menu import get_users_keyboard
from app.core.keyboards.base import Action
from app.core.keyboards.menu import (
    send_menu_keyboard,
)
from app.core.states.admin import AdminMenu

menu_router = Router()

logger = logging.getLogger(name="AdminMenu")


@menu_router.callback_query(
    AdminMenu.menu,
    isAdminCB(),
    AdminMenuCB.filter((F.action == Action.OPEN) & (F.target == AdminMenuTarget.USER)),
)
async def cb_open_users_menu(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await state.set_state(AdminMenu.Users.menu)
    await cb.message.edit_text("Пользователи", reply_markup=get_users_keyboard())  # type: ignore


@menu_router.callback_query(AdminMenu.menu, AdminMenuCB.filter(F.action == Action.BACK))
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_menu_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
