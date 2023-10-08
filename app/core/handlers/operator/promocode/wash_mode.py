from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.promocode.menu import send_promocode_keyboard
from app.core.keyboards.operator.promocode.mode import WashModeCB
from app.core.states.operator import OperatorMenu


wash_mode_router = Router()


@wash_mode_router.callback_query(
    OperatorMenu.Promocode.wash_mode,
    isOperatorCB(),
    WashModeCB.filter(F.action == Action.SELECT),
)
async def cb_select_mode(
    cb: types.CallbackQuery,
    callback_data: WashModeCB,
    state: FSMContext,
    session: AsyncSession,
):
    await cb.answer()
    await state.update_data(wash_mode=callback_data.wash_mode)
    await send_promocode_keyboard(cb.message.edit_text, state, session)  # type: ignore


@wash_mode_router.callback_query(
    OperatorMenu.Promocode.wash_mode,
    isOperatorCB(),
    WashModeCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    await cb.answer()
    await send_promocode_keyboard(cb.message.edit_text, state, session)  # type: ignore
