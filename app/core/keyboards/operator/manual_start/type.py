from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.utils.text import to_correct_message


class ManualStartReportTarget(IntEnum):
    TEST_MANUAL_START = auto()
    SERVICE_MANUAL_START = auto()
    REWASH_MANUAL_START = auto()
    PAID_MANUAL_START = auto()
    NONE = auto()


class ManualStartReportCB(CallbackData, prefix="mstart_report"):
    action: Action
    target: ManualStartReportTarget


def get_manual_start_type_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Тест",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.TEST_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Технический",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.SERVICE_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Перемывка",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.REWASH_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Оплата через эквайринг",
            callback_data=ManualStartReportCB(
                action=Action.OPEN, target=ManualStartReportTarget.PAID_MANUAL_START
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ManualStartReportCB(
                action=Action.BACK, target=ManualStartReportTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()


async def get_manual_start_text(state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    return to_correct_message(
        "Ручной запуск\n" f"*ID*: *{id}*\n" "\n" "Выберите тип ручного запуска:\n"
    )


async def send_manual_start_type_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    text = await get_manual_start_text(state)
    await state.set_state(OperatorMenu.ManualStart.type)
    await send_func(text=text, reply_markup=get_manual_start_type_keyboard())
