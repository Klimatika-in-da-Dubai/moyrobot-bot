from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.cleaning.cleaning import (
    CleaningMenuCB,
    CleaningMenuTarget,
)
from app.core.keyboards.operator.cleaning.place import send_place_menu
from app.core.keyboards.operator.menu import send_operator_menu_keyboard

from app.core.states.operator import OperatorMenu


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
    session: async_sessionmaker,
):
    await cb.answer()
    await state.update_data(place_id=callback_data.place_id)
    await send_place_menu(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Cleaning.menu,
    isOperatorCB(),
    CleaningMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Cleaning.menu,
    isOperatorCB(),
    CleaningMenuCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()