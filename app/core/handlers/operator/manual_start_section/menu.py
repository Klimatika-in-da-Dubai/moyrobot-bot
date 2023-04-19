from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import (
    ManualStartSectionCB,
    ManualStartSectionTarget,
)
from app.core.keyboards.operator.menu import (
    send_operator_menu_keyboard,
)
from app.core.states.operator import OperatorMenu

manual_start_menu_router = Router()


@manual_start_menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.menu,
    ManualStartSectionCB.filter(
        (F.action == Action.OPEN) & (F.target == ManualStartSectionTarget.MANUAL_START)
    ),
)
async def cb_manual_start_open(
    cb: types.CallbackQuery,
    state: FSMContext,
    callback_data: ManualStartSectionCB,
    session: async_sessionmaker,
):
    await state.update_data(id=callback_data.manual_start_id)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.menu,
    ManualStartSectionCB.filter(
        F.action == Action.BACK & F.target == ManualStartSectionTarget.NONE
    ),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()

    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
