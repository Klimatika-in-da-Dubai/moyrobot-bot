from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.menu import get_menu_keyboard
from app.core.keyboards.operator.manual_start.menu import get_manual_start_keyboard
from app.core.keyboards.operator.menu import OperatorMenuCB, OperatorMenuTarget

from app.core.states.operator import OperatorMenu


operator_menu_router = Router(name="operator-menu-router")


@operator_menu_router.callback_query(
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
    await state.set_state(OperatorMenu.ManualStartSection.menu)
    await cb.message.edit_text(  # type: ignore
        text="Ручные запуски", reply_markup=await get_manual_start_keyboard(session)
    )


@operator_menu_router.callback_query(
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
    await state.clear()
    await cb.message.edit_text(  # type: ignore
        text="Меню",
        reply_markup=await get_menu_keyboard(cb.message.chat.id, session),  # type: ignore
    )
