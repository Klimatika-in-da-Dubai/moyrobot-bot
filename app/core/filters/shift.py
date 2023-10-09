from aiogram import types
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.services.database.dao.shift import ShiftDAO


class isShiftOpenedCB(Filter):
    def __init__(self):
        pass

    async def __call__(
        self, cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
    ) -> bool:
        shiftdao = ShiftDAO(session=session)
        if not await shiftdao.is_shift_opened():
            await cb.answer("Смена закрыта", show_alert=True)
            await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
            return False

        return True


class isShiftClosedCB(Filter):
    def __init__(self):
        pass

    async def __call__(
        self, cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
    ) -> bool:
        shiftdao = ShiftDAO(session=session)
        if await shiftdao.is_shift_opened():
            await cb.answer("Смена открыта", show_alert=True)
            await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore
            return False

        return True
