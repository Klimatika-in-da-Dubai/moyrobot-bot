from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu


class OperatorMenuTarget(IntEnum):
    NONE = auto()
    MANUAL_START = auto()
    BONUS = auto()
    PROMOCODE = auto()
    ANTIFREEZE = auto()


class OperatorMenuCB(CallbackData, prefix="operator_menu"):
    action: Action
    target: OperatorMenuTarget


def get_operator_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Отчитаться по ручному запуску",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.MANUAL_START
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Выдать промокод",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.PROMOCODE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Начислить бонусы",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.BONUS
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Продать незамерзайку",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.ANTIFREEZE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=OperatorMenuCB(
                action=Action.BACK, target=OperatorMenuTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_operator_menu_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    await state.set_state(OperatorMenu.menu)
    await send_func("Меню оператора", reply_markup=get_operator_menu_keyboard())
