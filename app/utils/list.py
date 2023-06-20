from typing import Optional
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.database.dao.user import UserDAO
from app.services.database.models.user import User


async def get_selected_user(
    state: FSMContext, session: async_sessionmaker
) -> Optional[User]:
    data = await state.get_data()
    user_id = data.get("selected_user_id")
    if user_id is None:
        return None

    userdao = UserDAO(session=session)
    user = await userdao.get_by_id(user_id)
    return user
