from enum import IntEnum, auto
from typing import Literal
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.utils.promocode import get_promocode_info, get_promocode_text


Emoji = Literal["✅", "❌"]


class PromocodeMenuTarget(IntEnum):
    NONE = auto()
    PHONE = auto()
    WASH_MODE = auto()
    DESCRIPTION = auto()


class PromocodeMenuCB(CallbackData, prefix="promo"):
    action: Action
    target: PromocodeMenuTarget


async def get_promocode_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    phone, wash_mode, description = await get_promocode_info_status_emoji(state)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Номер телефона {phone}",
            callback_data=PromocodeMenuCB(
                action=Action.ENTER_TEXT, target=PromocodeMenuTarget.PHONE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Режим мойки {wash_mode}",
            callback_data=PromocodeMenuCB(
                action=Action.OPEN, target=PromocodeMenuTarget.WASH_MODE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Причина {description}",
            callback_data=PromocodeMenuCB(
                action=Action.ENTER_TEXT, target=PromocodeMenuTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=PromocodeMenuCB(
                action=Action.BACK, target=PromocodeMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=PromocodeMenuCB(
                action=Action.ENTER, target=PromocodeMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def get_promocode_info_status_emoji(
    state: FSMContext,
) -> tuple[Emoji, Emoji, Emoji]:
    phone, wash_mode, description = await get_promocode_info(state)

    phone_em = "✅" if phone is not None else "❌"
    wash_mode_em = "✅" if wash_mode is not None else "❌"
    description_em = "✅" if description is not None else "❌"

    return phone_em, wash_mode_em, description_em


async def send_promocode_keyboard(
    func, state: FSMContext, session: async_sessionmaker
) -> None:
    text = await get_promocode_text(state)
    await state.set_state(OperatorMenu.Promocode.menu)
    await func(text=text, reply_markup=await get_promocode_keyboard(state))
