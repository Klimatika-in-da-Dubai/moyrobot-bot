from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.utils.text import escape_chars


class ServiceManualStartTarget(IntEnum):
    DESCRIPTION = auto()
    PHOTO = auto()
    NONE = auto()


class ServiceManualStartCB(CallbackData, prefix="service_mstart"):
    action: Action
    target: ServiceManualStartTarget


def get_service_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Причина",
            callback_data=ServiceManualStartCB(
                action=Action.ENTER_TEXT,
                target=ServiceManualStartTarget.DESCRIPTION,
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Фото",
            callback_data=ServiceManualStartCB(
                action=Action.ADD_PHOTO, target=ServiceManualStartTarget.PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ServiceManualStartCB(
                action=Action.BACK,
                target=ServiceManualStartTarget.NONE,
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=ServiceManualStartCB(
                action=Action.ENTER, target=ServiceManualStartTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_manual_start_text(state: FSMContext):
    data = await state.get_data()

    id = escape_chars(data.get("id"))
    description = data.get("description")

    description_text = escape_chars(description) if description is not None else ""

    return (
        "Ручной запуск\n"
        "*Тип:* Технический\n"
        f"*ID:* {id}\n"
        f"*Причина:* {description_text}"
    )


async def send_service_manual_start_keyboard(
    send_func: Callable,
    state: FSMContext,
    session: AsyncSession,
):
    text = await get_manual_start_text(state)
    await state.set_state(OperatorMenu.ManualStart.ServiceManualStart.menu)
    await send_func(text=text, reply_markup=get_service_manual_start_keyboard())
