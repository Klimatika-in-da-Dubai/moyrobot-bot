from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.groups.menu import send_groups_menu
from app.core.keyboards.admin.groups.selected_group import (
    SelectedGroupCB,
    SelectedGroupTarget,
)
from app.core.keyboards.admin.mailing import send_mailing_selection_in_group_menu
from app.core.keyboards.base import Action

from app.core.states.admin import AdminMenu
from app.services.database.dao.group import GroupDAO
from app.utils.group import get_selected_group_id


select_router = Router()

select_router.callback_query.filter(AdminMenu.Groups.Selected.menu)


@select_router.callback_query(
    SelectedGroupCB.filter(F.target == SelectedGroupTarget.MAILING), isAdminCB()
)
async def cb_select_group(
    cb: CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker,
):
    await cb.answer()

    await send_mailing_selection_in_group_menu(cb.message.edit_text, state, session)  # type: ignore


@select_router.callback_query(
    SelectedGroupCB.filter(F.target == SelectedGroupTarget.DELETE), isAdminCB()
)
async def cb_delete_group(
    cb: CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker,
):
    await cb.answer()
    group_id = await get_selected_group_id(state)
    if group_id is None:
        await send_groups_menu(cb.message.edit_text, state, session)  # type: ignore
        return

    groupdao = GroupDAO(session)
    await groupdao.delete_group_by_id(group_id)
    await send_groups_menu(cb.message.edit_text, state, session)  # type: ignore


@select_router.callback_query(
    SelectedGroupCB.filter(F.target == Action.BACK), isAdminCB()
)
async def cb_back(cb: CallbackQuery, state: FSMContext, session: async_sessionmaker):
    await cb.answer()
    await send_groups_menu(cb.message.edit_text, state, session)  # type: ignore
