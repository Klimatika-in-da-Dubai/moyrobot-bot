from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu


class TestManualStartTarget(IntEnum):
    NONE = auto()
    DESCRIPTION = auto()


class TestManualStartCB(CallbackData, prefix="test_mstart"):
    action: Action
    target: TestManualStartTarget


def get_test_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Причина запуска",
            callback_data=TestManualStartCB(
                action=Action.ENTER_TEXT, target=TestManualStartTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=TestManualStartCB(
                action=Action.BACK, target=TestManualStartTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=TestManualStartCB(
                action=Action.ENTER, target=TestManualStartTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def get_manual_start_text(state: FSMContext):
    data = await state.get_data()

    id = data.get("id")
    description = data.get("description")
    description_text = description if description is not None else ""
    return (
        "Ручной запуск\n"
        "*Тип:* Тест\n"
        f"*ID:* {id}\n"
        f"*Причина:* {description_text}"
    )


async def send_test_manual_start_keyboard(
    send_func: Callable,
    state: FSMContext,
    session: async_sessionmaker,
):
    text = await get_manual_start_text(state)
    await state.set_state(OperatorMenu.ManualStartSection.TestManualStart.menu)
    await send_func(text=text, reply_markup=get_test_manual_start_keyboard())
