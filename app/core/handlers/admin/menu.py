from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

import logging
from app.core.filters.admin import isAdminCB

from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action
from app.core.keyboards.menu import get_menu_keyboard
from app.core.keyboards.admin.menu import (
    AdminMenuCB,
    AdminMenuTarget,
)
from app.core.keyboards.admin.users_section.menu import get_users_keyboard


menu_router = Router()

logger = logging.getLogger(name="AdminMenu")


@menu_router.callback_query(
    isAdminCB(),
    AdminMenu.menu,
    AdminMenuCB.filter((F.action == Action.OPEN) & (F.target == AdminMenuTarget.USER)),
)
async def cb_open_users_menu(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await state.set_state(AdminMenu.UsersSection.menu)
    await cb.message.edit_text("Пользователи", reply_markup=get_users_keyboard())  # type: ignore


@menu_router.callback_query(AdminMenu.menu, AdminMenuCB.filter(F.action == Action.BACK))
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.clear()
    await cb.message.edit_text(  # type: ignore
        text="Меню",
        reply_markup=await get_menu_keyboard(cb.message.chat.id, session),  # type: ignore
    )
