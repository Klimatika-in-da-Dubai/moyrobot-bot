from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dto.cleaning import CleaningDTO


class CleaningMenuTarget(IntEnum):
    PLACE = auto()
    NONE = auto()


class CleaningMenuCB(CallbackData, prefix="cleaning"):
    action: Action
    target: CleaningMenuTarget
    place_id: int


def get_cleaning_keboard(cleaning: CleaningDTO):
    builder = InlineKeyboardBuilder()

    for i, place in enumerate(cleaning.places):
        emoji = "✅" if place.is_filled() else "❌"
        builder.row(
            types.InlineKeyboardButton(
                text=f"{place.name} {emoji}",
                callback_data=CleaningMenuCB(
                    action=Action.OPEN, target=CleaningMenuTarget.PLACE, place_id=i
                ).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=CleaningMenuCB(
                action=Action.BACK, target=CleaningMenuTarget.NONE, place_id=-1
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=CleaningMenuCB(
                action=Action.ENTER, target=CleaningMenuTarget.NONE, place_id=-1
            ).pack(),
        ),
    )
    return builder.as_markup()


async def send_cleaning_menu(func, state: FSMContext, session: AsyncSession):
    await state.update_data(place_id=None)
    data = await state.get_data()
    cleaning = CleaningDTO.from_dict(data)
    await func(text="Места уборки", reply_markup=get_cleaning_keboard(cleaning))
    await state.set_state(OperatorMenu.Cleaning.menu)
