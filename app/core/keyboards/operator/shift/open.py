from dataclasses import dataclass
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
from app.utils.shift import get_open_shift


class OpenShiftMenuTarget(IntEnum):
    CLEANING_CHECK = auto()
    NONE = auto()


class OpenShiftMenuCB(CallbackData, prefix="open_shift"):
    action: Action
    target: OpenShiftMenuTarget


@dataclass
class OpenShiftEmojis:
    cleaning: Literal["👍", "👎"]


def get_open_shift_keyboard(shift: OpenShift) -> types.InlineKeyboardMarkup:
    builder = get_shift_menu_builder(shift)

    emojis = get_open_shift_emojis(shift)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Качество уборки {emojis.cleaning}",
            callback_data=OpenShiftMenuCB(
                action=Action.SELECT, target=OpenShiftMenuTarget.CLEANING_CHECK
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=OpenShiftMenuCB(
                action=Action.BACK, target=OpenShiftMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=OpenShiftMenuCB(
                action=Action.ENTER, target=OpenShiftMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


def get_open_shift_emojis(shift: OpenShift):
    cleaning = "👍" if shift.cleaning_check else "👎"
    return OpenShiftEmojis(cleaning=cleaning)


async def send_open_shift_menu_keyboard(
    func, state: FSMContext, session: async_sessionmaker
):
    shift = await get_open_shift(state)

    await state.set_state(OperatorMenu.Shift.menu)
    await func(text="Открытие смены", reply_markup=get_open_shift_keyboard(shift))
