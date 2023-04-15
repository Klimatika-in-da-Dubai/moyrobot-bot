from aiogram import types
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.menu import get_menu_keyboard
from app.services.database.dao.user import UserDAO

from app.services.database.models.user import Role


class isAdminCB(Filter):
    def __init__(self):
        self.role = Role.ADMIN

    async def __call__(
        self, cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
    ) -> bool:
        userdao = UserDAO(session=session)
        if not await userdao.exists(chat_id=cb.message.chat.id):  # type: ignore
            return False

        if await userdao.is_admin(chat_id=cb.message.chat.id):  # type: ignore
            return True

        await cb.answer(text="Вы не являетесь админом", show_alert=True)
        await state.clear()
        await cb.message.edit_text(  # type: ignore
            text="Меню",
            reply_markup=await get_menu_keyboard(cb.message.chat.id, session),  # type: ignore
        )
        return False