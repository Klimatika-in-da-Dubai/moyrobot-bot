from aiogram import types
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.menu import get_menu_keyboard, send_menu_keyboard
from app.services.database.dao.user import UserDAO

from app.services.database.models.user import Role


class isOperatorCB(Filter):
    def __init__(self):
        self.role = Role.ADMIN

    async def __call__(
        self, cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
    ) -> bool:
        userdao = UserDAO(session=session)
        if not await userdao.exists(chat_id=cb.message.chat.id):  # type: ignore
            await send_menu_keyboard(cb.message.answer, state, session)  # type: ignore
            return False

        if not await userdao.is_operator(chat_id=cb.message.chat.id):  # type: ignore
            await cb.answer(text="Вы не являетесь оператором", show_alert=True)

            await send_menu_keyboard(cb.message.answer, state, session)  # type: ignore
            return False

        return True
