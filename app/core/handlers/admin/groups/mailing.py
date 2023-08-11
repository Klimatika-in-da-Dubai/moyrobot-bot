from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.groups.menu import send_groups_menu
from app.core.keyboards.admin.groups.selected_group import send_selected_group_menu
from app.core.keyboards.admin.mailing import (
    MailingSelectionCB,
    get_group_mailings,
    send_mailing_selection_in_change_menu,
    send_mailing_selection_in_group_menu,
)

from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action
from app.services.database.dao.group import GroupDAO
from app.services.database.dao.mailing import GroupMailingDAO


from app.services.database.models.mailing import MailingType
from app.utils.group import (
    clear_mailings,
    get_mailings_from_state,
    get_selected_group_id,
)

mailing_router = Router()

mailing_router.callback_query(AdminMenu.Groups.Selected.mailing)


@mailing_router.callback_query(
    isAdminCB(),
    MailingSelectionCB.filter(
        F.action == Action.SELECT,
    ),
)
async def cb_select_mailing(
    cb: types.CallbackQuery,
    callback_data: MailingSelectionCB,
    state: FSMContext,
    session: async_sessionmaker,
):
    await select_mailing(state, callback_data.mailing)
    await send_mailing_selection_in_group_menu(cb.message.edit_text, state, session)  # type: ignore


async def select_mailing(state: FSMContext, mailing: MailingType):
    data = await state.get_data()
    mailings = data.get("mailings")

    if not isinstance(mailings, list):
        raise ValueError("Mailings in state data is not the list")

    if mailing in mailings:
        mailings.remove(mailing)
    else:
        mailings.append(mailing)

    await state.update_data(mailings=mailings)


@mailing_router.callback_query(
    isAdminCB(),
    MailingSelectionCB.filter(
        F.action == Action.ENTER,
    ),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    group_id = await get_selected_group_id(state)
    if group_id is None:
        await cb.answer("Данная группа не существует")
        await send_groups_menu(cb.message.edit_text, state, session)  # type: ignore
        return

    mailings = await get_mailings_from_state(state)
    await update_group_mailings(group_id, mailings, session)
    await clear_mailings(state)
    await send_selected_group_menu(cb.message.edit_text, state, session)  # type: ignore


async def update_group_mailings(
    group_id: int, mailings: list[MailingType], session: async_sessionmaker
):
    groupdao = GroupDAO(session)
    groupmailingdao = GroupMailingDAO(session)
    group = await groupdao.get_by_id(group_id)
    if group is None:
        raise ValueError("Group not found")

    await groupmailingdao.update_group_mailings(group, mailings)
