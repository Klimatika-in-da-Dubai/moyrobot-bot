from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.cleaning.cleaning import (
    CleaningMenuCB,
    CleaningMenuTarget,
)
from app.core.keyboards.operator.cleaning.place import send_place_menu
from app.core.keyboards.operator.menu import send_operator_menu_keyboard

from app.core.states.operator import OperatorMenu
from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.dto.cleaning import CleaningDTO
from app.services.database.models.cleaning import Cleaning


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Cleaning.menu,
    isOperatorCB(),
    CleaningMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == CleaningMenuTarget.PLACE)
    ),
)
async def cb_open_place(
    cb: types.CallbackQuery,
    callback_data: CleaningMenuCB,
    state: FSMContext,
    session: AsyncSession,
):
    await cb.answer()
    await state.update_data(place_id=callback_data.place_id)
    await send_place_menu(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Cleaning.menu,
    isOperatorCB(),
    CleaningMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Cleaning.menu,
    isOperatorCB(),
    CleaningMenuCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    cleaningdto = CleaningDTO.from_dict(data)
    if not cleaningdto.is_filled():
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    cleaningdao = CleaningDAO(session)
    cleaning = Cleaning(cleaning=cleaningdto.to_dict())
    await cleaningdao.add_cleaning(cleaning)
    await state.update_data(cleaning=None)
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
