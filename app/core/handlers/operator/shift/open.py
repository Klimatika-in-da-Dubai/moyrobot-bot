from datetime import datetime
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.filters.shift import isShiftClosedCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.keyboards.operator.shift.open import OpenShiftMenuCB, OpenShiftMenuTarget

from app.core.states.operator import OperatorMenu
from app.services.database.dao.shift import OpenShiftDAO, ShiftDAO
from app.services.database.models.shift import Shift
from app.utils.shift import get_open_shift


open_shift_router = Router()


@open_shift_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    OpenShiftMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == OpenShiftMenuTarget.CLEANING_CHECK)
    ),
)
async def cb_cleaning_check(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    shift = await get_open_shift(state)
    await state.update_data(cleaning_check=not shift.cleaning_check)
    await send_shift_keyboard(cb.message.edit_text, state, session)  # type: ignore


@open_shift_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    OpenShiftMenuCB.filter(F.action == Action.ENTER),
    isShiftClosedCB(),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    shiftdao = ShiftDAO(session)
    openshiftdao = OpenShiftDAO(session)

    await shiftdao.add_shift(
        Shift(opened_by_id=cb.message.chat.id, open_date=datetime.now())  # type: ignore
    )
    shift = await shiftdao.get_last_shift()

    if shift is None:
        await cb.answer(
            text=(
                "Произошла ошибка. Невозможно добавить новую смену."
                "Сообщите администратору"
            ),
            show_alert=True,
        )
        return

    openshift = await get_open_shift(state)
    openshift.id = shift.id
    openshift.date = shift.open_date
    await openshiftdao.add_shift(openshift)
    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
