from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.admin.groups.menu import GroupsMenuCB
from app.core.keyboards.admin.groups.selected_group import send_selected_group_menu
from app.core.keyboards.admin.menu import send_admin_menu
from app.utils.group import set_selected_group_id
from app.core.keyboards.base import Action

from app.core.states.admin import AdminMenu


menu_router = Router()

menu_router.callback_query(AdminMenu.Groups.menu)


@menu_router.callback_query(GroupsMenuCB.filter(F.action == Action.OPEN))
async def cb_select_group(
    cb: CallbackQuery,
    callback_data: GroupsMenuCB,
    state: FSMContext,
    session: async_sessionmaker,
):
    await cb.answer()
    await set_selected_group_id(state, callback_data.group_id)
    await send_selected_group_menu(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(GroupsMenuCB.filter(F.action == Action.BACK))
async def cb_back(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_admin_menu(cb.message.edit_text, state)  # type: ignore
