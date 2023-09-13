from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dao.corporation import CorporationDAO
from app.utils.text import escape_chars


class CorporateManualStartTarget(IntEnum):
    NONE = auto()
    DESCRIPTION = auto()
    PHOTO = auto()
    CORPORATION = auto()


class CorporateManualStartCB(CallbackData, prefix="corporate_mstart"):
    action: Action
    target: CorporateManualStartTarget


def get_test_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Причина запуска",
            callback_data=CorporateManualStartCB(
                action=Action.ENTER_TEXT,
                target=CorporateManualStartTarget.DESCRIPTION,
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Фото",
            callback_data=CorporateManualStartCB(
                action=Action.ADD_PHOTO, target=CorporateManualStartTarget.PHOTO
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Компании",
            callback_data=CorporateManualStartCB(
                action=Action.OPEN, target=CorporateManualStartTarget.CORPORATION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=CorporateManualStartCB(
                action=Action.BACK, target=CorporateManualStartTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=CorporateManualStartCB(
                action=Action.ENTER, target=CorporateManualStartTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def get_manual_start_text(state: FSMContext, session: async_sessionmaker):
    data = await state.get_data()

    id = escape_chars(data.get("id"))
    description = data.get("description")
    corporation_name = await get_corporation_name(data, session)

    description_text = escape_chars(description) if description is not None else ""
    return (
        "Ручной запуск\n"
        "*Тип:* Копроративный\n"
        f"*ID:* {id}\n"
        f"*Компания*: {corporation_name}\n"
        f"*Причина:* {description_text}"
    )


async def get_corporation_name(data: dict, session: async_sessionmaker) -> str:
    corporation_id = data.get("corporation_id")
    if corporation_id is None:
        return ""
    corporation = await CorporationDAO(session).get_by_id(id_=corporation_id)
    if corporation is None:
        raise ValueError(f"No such corporation in database with id={corporation_id}")
    return escape_chars(corporation.name)


async def send_corporate_manual_start_keyboard(
    send_func: Callable,
    state: FSMContext,
    session: async_sessionmaker,
):
    text = await get_manual_start_text(state, session)
    await state.set_state(OperatorMenu.ManualStart.CorporateManualStart.menu)
    await send_func(text=text, reply_markup=get_test_manual_start_keyboard())
