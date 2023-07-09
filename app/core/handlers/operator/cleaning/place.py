from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, get_cancel_keyboard
from app.core.keyboards.operator.cleaning.cleaning import (
    send_cleaning_menu,
)
from app.core.keyboards.operator.cleaning.place import (
    PlaceMenuCB,
    PlaceMenuTarget,
)

from app.core.states.operator import OperatorMenu
from app.utils.cleaning import get_current_work


place_router = Router()


@place_router.callback_query(
    OperatorMenu.Cleaning.Place.menu,
    isOperatorCB(),
    PlaceMenuCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == PlaceMenuTarget.WORK)
    ),
)
async def cb_work_add_photo(
    cb: types.CallbackQuery,
    callback_data: PlaceMenuCB,
    state: FSMContext,
):
    await cb.answer()

    await state.update_data(work_id=callback_data.work_id)
    await state.set_state(OperatorMenu.Cleaning.Place.Work.photo)
    await cb.message.edit_text(  # type: ignore
        "Пришлите фото уборки", reply_markup=get_cancel_keyboard()
    )


@place_router.callback_query(
    OperatorMenu.Cleaning.Place.menu,
    isOperatorCB(),
    PlaceMenuCB.filter((F.action == Action.OPEN) & (F.target == PlaceMenuTarget.WORK)),
)
async def cb_work_open(
    cb: types.CallbackQuery,
    callback_data: PlaceMenuCB,
    state: FSMContext,
):
    await cb.answer()
    await state.update_data(work_id=callback_data.work_id)
    await state.set_state(OperatorMenu.Cleaning.Place.Work.photo)

    work = await get_current_work(state)
    await cb.message.delete()  # type: ignore
    await cb.message.answer_photo(  # type: ignore
        photo=work.photo_file_id,
        caption="Можете изменить фото уборки\n\\(Для этого отправьте фото\\)",
        reply_markup=get_cancel_keyboard(),
    )


@place_router.callback_query(
    OperatorMenu.Cleaning.Place.menu,
    isOperatorCB(),
    PlaceMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_cleaning_menu(cb.message.edit_text, state, session)  # type: ignore
