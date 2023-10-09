from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import (
    ManualStartCB,
    ManualStartTarget,
)
from app.core.keyboards.operator.menu import (
    send_operator_menu_keyboard,
)
from app.core.states.operator import OperatorMenu

manual_start_menu_router = Router()


@manual_start_menu_router.callback_query(
    OperatorMenu.ManualStart.menu,
    isOperatorCB(),
    ManualStartCB.filter(
        (F.action == Action.OPEN) & (F.target == ManualStartTarget.MANUAL_START)
    ),
)
async def cb_manual_start_open(
    cb: types.CallbackQuery,
    state: FSMContext,
    callback_data: ManualStartCB,
    session: AsyncSession,
):
    await state.update_data(id=callback_data.manual_start_id)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_menu_router.callback_query(
    OperatorMenu.ManualStart.menu,
    isOperatorCB(),
    ManualStartCB.filter(F.action == Action.BACK & F.target == ManualStartTarget.NONE),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()

    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
