from typing import Optional
from aiogram.fsm.context import FSMContext

from app.services.database.models.mailing import MailingType


async def set_selected_group_id(state: FSMContext, group_id: int | None) -> None:
    await state.update_data(selected_group_id=group_id)


async def get_selected_group_id(state: FSMContext) -> Optional[int]:
    data = await state.get_data()
    return data.get("selected_group_id")


async def unselect_group(state: FSMContext) -> None:
    await set_selected_group_id(state, None)


async def get_mailings_from_state(state: FSMContext) -> list[MailingType]:
    data = await state.get_data()
    mailings = data.get("mailings")
    if mailings is None:
        return []
    return mailings


async def clear_mailings(state: FSMContext) -> None:
    await state.update_data(mailings=None)
