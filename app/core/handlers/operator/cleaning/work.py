from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.cleaning.place import (
    send_place_menu,
)
from app.core.keyboards.operator.cleaning.work import WorkMenuCB, WorkMenuTarget

from app.core.states.operator import OperatorMenu
from app.services.database.dto.cleaning import CleaningDTO
from app.utils.cleaning import get_place_id, get_work_id


work_router = Router()


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.menu,
    isOperatorCB(),
    WorkMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == WorkMenuTarget.CHANGE_PHOTO)
    ),
)
@work_router.message(OperatorMenu.Cleaning.Place.Work.photo, F.photo)
async def message_work_photo(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    data = await state.get_data()
    cleaning = CleaningDTO.from_dict(data)
    place_id = await get_place_id(state)
    work_id = await get_work_id(state)
    work = cleaning.places[place_id].works[work_id]
    work.photo_file_id = message.photo[-1].file_id  # type: ignore
    await state.update_data(cleaning=cleaning.to_dict())
    await send_place_menu(message.answer, state, session)


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.photo,
    isOperatorCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
    F.message.text,
)
async def cb_cancel(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_place_menu(cb.message.edit_text, state, session)  # type: ignore


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.photo,
    isOperatorCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
    F.message.photo,
)
async def cb_cancel_with_photo(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await cb.message.delete()  # type: ignore
    await send_place_menu(cb.message.answer, state, session)  # type: ignore
