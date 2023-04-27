from token import OP
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.menu import send_menu_keyboard
from app.core.keyboards.operator.antifreeze.menu import send_antifreeze_keyboard
from app.core.keyboards.operator.bonus.menu import send_bonus_keyboard
from app.core.keyboards.operator.manual_start.menu import (
    send_manual_starts_keyboard,
)
from app.core.keyboards.operator.menu import OperatorMenuCB, OperatorMenuTarget
from app.core.keyboards.operator.promocode.menu import send_promocode_keyboard
from app.core.states.operator import OperatorMenu

menu_router = Router(name="operator-menu-router")


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.menu,
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.MANUAL_START)
    ),
)
async def cb_manual_start_open(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.menu,
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.PROMOCODE)
    ),
)
async def cb_promocode(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_promocode_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.menu,
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.BONUS)
    ),
)
async def cb_bonus(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_bonus_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.menu,
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.ANTIFREEZE)
    ),
)
async def cb_antifreeze(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_antifreeze_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.menu,
    OperatorMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_menu_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
