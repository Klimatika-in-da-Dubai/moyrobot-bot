from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.users.mailing import (
    MailingSelectionCB,
    send_mailing_selection,
)

from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action


from app.core.keyboards.admin.users.add.add import (
    send_add_user_menu,
)
from app.services.database.models.mailing import MailingType

mailing_router = Router()


@mailing_router.callback_query(
    AdminMenu.Users.Add.mailing,
    isAdminCB(),
    MailingSelectionCB.filter(
        F.action == Action.SELECT,
    ),
)
async def cb_select_mailing(
    cb: types.CallbackQuery, callback_data: MailingSelectionCB, state: FSMContext
):
    await select_mailing(state, callback_data.mailing)
    await send_mailing_selection(cb.message.edit_text, state)  # type: ignore


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
    AdminMenu.Users.Add.mailing,
    isAdminCB(),
    MailingSelectionCB.filter(
        F.action == Action.ENTER,
    ),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await send_add_user_menu(cb.message.edit_text, state)  # type: ignore
