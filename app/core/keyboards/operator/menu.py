from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dao.shift import ShiftDAO


class OperatorMenuTarget(IntEnum):
    NONE = auto()
    OPEN_SHIFT = auto()
    CLOSE_SHIFT = auto()
    MANUAL_START = auto()
    BONUS = auto()
    PROMOCODE = auto()
    ANTIFREEZE = auto()


class OperatorMenuCB(CallbackData, prefix="operator_menu"):
    action: Action
    target: OperatorMenuTarget


def get_opened_operator_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Закрыть смену",
            callback_data=OperatorMenuCB(
                action=Action.OPEN, target=OperatorMenuTarget.CLOSE_SHIFT
            ).pack(),
        )
    )

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


def get_closed_operator_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Открыть смену",
            callback_data=OperatorMenuCB(
                action=Action.OPEN,
                target=OperatorMenuTarget.OPEN_SHIFT,
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_operator_menu_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    await state.set_state(OperatorMenu.menu)
    shiftdao = ShiftDAO(session)

    if await shiftdao.is_shift_opened():
        reply_markup = get_opened_operator_menu_keyboard()
    else:
        reply_markup = get_closed_operator_menu_keyboard()
    await send_func(
        "Меню оператора",
        reply_markup=reply_markup,
    )
