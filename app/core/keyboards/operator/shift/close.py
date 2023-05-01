from enum import IntEnum, auto
from typing import Literal

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.operator.shift.base import (
    get_shift_menu_builder,
)
from app.core.states.operator import OperatorMenu
from app.services.database.models.shift import OpenShift
from app.utils.shift import get_close_shift


class CloseShiftMenuTarget(IntEnum):
    NONE = auto()


class CloseShiftMenuCB(CallbackData, prefix="open_shift"):
    action: Action
    target: CloseShiftMenuTarget


def get_close_shift_keyboard(shift: OpenShift) -> types.InlineKeyboardMarkup:
    builder = get_shift_menu_builder(shift)

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=CloseShiftMenuCB(
                action=Action.BACK, target=CloseShiftMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=CloseShiftMenuCB(
                action=Action.ENTER, target=CloseShiftMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def send_close_shift_menu_keyboard(
    func, state: FSMContext, session: async_sessionmaker
):
    shift = await get_close_shift(state)

    await state.set_state(OperatorMenu.Shift.menu)
    await func(text="Открытие смены", reply_markup=get_close_shift_keyboard(shift))
