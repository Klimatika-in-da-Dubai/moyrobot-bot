from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu


class RewashManualStartTarget(IntEnum):
    PHOTO = auto()
    DESCRIPTION = auto()
    NONE = auto()


class RewashManualStartCB(CallbackData, prefix="service_mstart"):
    action: Action
    target: RewashManualStartTarget


def get_rewash_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Фото",
            callback_data=RewashManualStartCB(
                action=Action.ADD_PHOTO, target=RewashManualStartTarget.PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Причина перемывки",
            callback_data=RewashManualStartCB(
                action=Action.ENTER_TEXT, target=RewashManualStartTarget.DESCRIPTION
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=RewashManualStartCB(
                action=Action.BACK, target=RewashManualStartTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=RewashManualStartCB(
                action=Action.ENTER, target=RewashManualStartTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_manual_start_text(state: FSMContext):
    data = await state.get_data()

    id = data.get("id")
    photo_file_id = data.get("photo_file_id")
    description = data.get("description")

    photo_status = "✅" if photo_file_id is not None else "❌"
    description_text = description if description is not None else ""

    return (
        "Ручной запуск\n"
        "*Тип:* Перемывка\n"
        f"*ID:* {id}\n"
        f"*Фото:* {photo_status}\n"
        f"*Причина перемывки:* {description_text}"
    )


async def send_rewash_manual_start_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    text = await get_manual_start_text(state)
    await state.set_state(OperatorMenu.ManualStartSection.RewashManualStart.menu)
    await send_func(text=text, reply_markup=get_rewash_manual_start_keyboard())
