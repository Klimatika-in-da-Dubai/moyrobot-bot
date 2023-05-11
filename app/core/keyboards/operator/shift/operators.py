from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import User


class OperatorsCB(CallbackData, prefix="operators"):
    action: Action
    id: int


def get_operators_keyboard(operators: list[User]):
    builder = InlineKeyboardBuilder()
    for op in operators:
        builder.row(
            types.InlineKeyboardButton(
                text=f"{op.name}",
                callback_data=OperatorsCB(action=Action.SELECT, id=op.id).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=OperatorsCB(action=Action.BACK, id=-1).pack(),
        )
    )
    return builder.as_markup()


async def send_operators_keyboard(func, state: FSMContext, session: async_sessionmaker):
    userdao = UserDAO(session)
    operators = await userdao.get_operators()
    await func(text="Выберите имя", reply_markup=get_operators_keyboard(operators))
    await state.set_state(OperatorMenu.Shift.operator_name)
