from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.operator.shift.close import send_close_shift_menu_keyboard
from app.core.keyboards.operator.shift.open import send_open_shift_menu_keyboard

from app.services.database.dao.shift import ShiftDAO


async def send_shift_keyboard(func, state: FSMContext, session: async_sessionmaker):
    shiftdao = ShiftDAO(session)
    if await shiftdao.is_shift_opened():
        await send_close_shift_menu_keyboard(func, state, session)  # type: ignore
    else:
        await send_open_shift_menu_keyboard(func, state, session)  # type: ignore
