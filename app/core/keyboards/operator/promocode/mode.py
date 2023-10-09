from aiogram import types

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.models.promocode import WashMode
from app.utils.promocode import get_promocode_text


class WashModeCB(CallbackData, prefix="wash_mode"):
    action: Action
    wash_mode: WashMode


def get_wash_mode_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Режим 1",
            callback_data=WashModeCB(
                action=Action.SELECT, wash_mode=WashMode.MODE1
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Режим 2",
            callback_data=WashModeCB(
                action=Action.SELECT, wash_mode=WashMode.MODE2
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Режим 3",
            callback_data=WashModeCB(
                action=Action.SELECT, wash_mode=WashMode.MODE3
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Режим 4",
            callback_data=WashModeCB(
                action=Action.SELECT, wash_mode=WashMode.MODE4
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=WashModeCB(
                action=Action.BACK, wash_mode=WashMode.NONE
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_washmode_keyboard(func, state: FSMContext, session: AsyncSession):
    text = await get_promocode_text(state)
    await state.set_state(OperatorMenu.Promocode.wash_mode)
    await func(text=text, reply_markup=get_wash_mode_keyboard())
