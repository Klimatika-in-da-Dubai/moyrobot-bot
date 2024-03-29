from datetime import datetime
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.filters.operator import isOperatorCB
from app.core.filters.shift import isShiftOpenedCB
from app.core.handlers.operator.shift.utils import check_for_consumables
from app.core.keyboards.base import Action
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.shift.close import (
    CloseShiftMenuCB,
)

from app.core.states.operator import OperatorMenu
from app.services.checker.shift.shift import ShiftChecker
from app.services.database.dao.shift import CloseShiftDAO, ShiftDAO
from app.utils.shift import get_close_shift, get_operator_id


close_shift_router = Router()


@close_shift_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    CloseShiftMenuCB.filter(F.action == Action.ENTER),
    isShiftOpenedCB(),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    closed_by_id = await get_operator_id(state)
    if closed_by_id is None:
        await cb.answer("Выберите оператора", show_alert=True)
        return

    shiftdao = ShiftDAO(session)
    shift = await shiftdao.get_last_shift()

    if shift is None:
        await cb.answer(
            text=(
                "Произошла ошибка. Невозможно закрыть смену." "Сообщите администратору"
            ),
            show_alert=True,
        )
        return

    await cb.answer()
    shift.close_date = datetime.now()
    shift.closed_by_id = closed_by_id
    await shiftdao.add_shift(shift)

    close_shift = await get_close_shift(state)
    close_shift.id = shift.id
    close_shift.date = shift.close_date
    closeshiftdao = CloseShiftDAO(session)
    await closeshiftdao.add_shift(close_shift)

    await ShiftChecker(session).check(shift)

    await check_for_consumables(close_shift, session)

    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
