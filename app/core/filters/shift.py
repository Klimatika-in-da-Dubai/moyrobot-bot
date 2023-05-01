from aiogram import types
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.menu import send_menu_keyboard
from app.services.database.dao.shift import ShiftDAO

from app.services.database.models.user import Role


class isShiftOpenedCB(Filter):
    def __init__(self):
        pass

    async def __call__(
        self, cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
    ) -> bool:
        shiftdao = ShiftDAO(session=session)
        if await shiftdao.is_shift_opened():
            return True

        return False
