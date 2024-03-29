from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.operator.shift.close import send_close_shift_menu_keyboard
from app.core.keyboards.operator.shift.open import send_open_shift_menu_keyboard

from app.services.database.dao.shift import ShiftDAO
from app.services.database.dao.user import UserDAO
from app.utils.shift import get_operator_id


async def send_shift_keyboard(
    func, message: types.Message, state: FSMContext, session: AsyncSession
):
    shiftdao = ShiftDAO(session)
    userdao = UserDAO(session)

    if not await UserDAO(session).is_work_account(message.chat.id):
        await state.update_data(operator_id=message.chat.id)

    operator_id = await get_operator_id(state)
    if operator_id is not None:
        operator_name = await userdao.get_user_name_by_id(operator_id)
        await state.update_data(operator_name=operator_name)

    if await shiftdao.is_shift_opened():
        await send_close_shift_menu_keyboard(func, state, session)  # type: ignore
    else:
        await send_open_shift_menu_keyboard(func, state, session)  # type: ignore
