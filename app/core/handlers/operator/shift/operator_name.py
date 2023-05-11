from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.keyboards.operator.shift.operators import OperatorsCB

from app.core.states.operator import OperatorMenu


operator_name_router = Router()


@operator_name_router.callback_query(
    OperatorMenu.Shift.operator_name,
    isOperatorCB(),
    OperatorsCB.filter(F.action == Action.SELECT),
)
async def cb_select_operator_name(
    cb: types.CallbackQuery,
    callback_data: OperatorsCB,
    state: FSMContext,
    session: async_sessionmaker,
):
    await state.update_data(operator_id=callback_data.id)
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@operator_name_router.callback_query(
    OperatorMenu.Shift.operator_name,
    isOperatorCB(),
    OperatorsCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
