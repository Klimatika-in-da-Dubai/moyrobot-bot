from aiogram import F, Router, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.shift.base import ShiftMenuCB
from app.core.keyboards.operator.shift.close import CloseShiftMenuCB
from app.core.keyboards.operator.shift.open import OpenShiftMenuCB
from app.core.states.operator import OperatorMenu


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    or_f(
        OpenShiftMenuCB.filter(F.action == Action.BACK),
        CloseShiftMenuCB.filter(F.action == Action.BACK),
    ),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
