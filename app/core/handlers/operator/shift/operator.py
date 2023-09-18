from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.keyboards.operator.shift.operator import OperatorsCB

from app.core.states.operator import OperatorMenu
from app.services.database.dao.user import UserDAO
from app.utils.shift import get_operator_id


operator_selection_router = Router()


@operator_selection_router.callback_query(
    OperatorMenu.Shift.operator,
    isOperatorCB(),
    OperatorsCB.filter(F.action == Action.SELECT),
)
async def cb_select_operator_name(
    cb: types.CallbackQuery,
    callback_data: OperatorsCB,
    state: FSMContext,
    session: async_sessionmaker,
):
    await cb.answer()
    userdao = UserDAO(session)
    operator_name = await userdao.get_user_name_by_id(callback_data.id)
    await state.update_data(operator_id=callback_data.id)
    await state.set_state(OperatorMenu.Shift.auth)

    await cb.message.edit_text(  # type: ignore
        f"Введите пинкод {operator_name}", reply_markup=get_cancel_keyboard()
    )


@operator_selection_router.message(OperatorMenu.Shift.auth, F.text)
async def message_pincode(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    if not message.text.isdigit():  # type: ignore
        await message.answer("Введите число\\!", reply_markup=get_cancel_keyboard())
        return

    pincode = message.text
    userdao = UserDAO(session)

    operator_id = await get_operator_id(state)
    if operator_id is None:
        await message.answer("Ошибка в получении id оператора")
        await send_shift_keyboard(message.edit_text, message, state, session)  # type: ignore
        return

    if not await userdao.get_pincode(operator_id) == pincode:
        await message.answer("Неверный пинкод\\!", reply_markup=get_cancel_keyboard())
        return

    await send_shift_keyboard(message.answer, message, state, session)  # type: ignore


@operator_selection_router.callback_query(OperatorMenu.Shift.auth, CancelCB.filter())
async def cb_cancel(cb: CallbackQuery, state: FSMContext, session: async_sessionmaker):
    await cb.answer()
    await state.update_data(operator_id=None)
    await send_shift_keyboard(cb.message.answer, cb.message, state, session)  # type: ignore


@operator_selection_router.callback_query(
    OperatorMenu.Shift.operator,
    isOperatorCB(),
    OperatorsCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
