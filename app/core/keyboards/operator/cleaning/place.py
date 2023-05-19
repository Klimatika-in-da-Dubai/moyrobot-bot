from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.keyboards.operator.cleaning.cleaning import CleaningMenuCB
from app.core.states.operator import OperatorMenu
from app.services.database.dto.cleaning import CleaningDTO, Place
from app.utils.cleaning import get_place_id
from app.utils.text import escape_chars


class PlaceMenuTarget(IntEnum):
    WORK = auto()
    NONE = auto()


class PlaceMenuCB(CallbackData, prefix="place"):
    action: Action
    target: PlaceMenuTarget
    work_id: int


def get_place_keyboard(place: Place):
    builder = InlineKeyboardBuilder()

    for i, work in enumerate(place.works):
        emoji = "✅" if work.is_filled() else "❌"
        action = Action.OPEN if work.is_filled() else Action.ADD_PHOTO
        builder.row(
            types.InlineKeyboardButton(
                text=f"{work.name} {emoji}",
                callback_data=PlaceMenuCB(
                    action=action, target=PlaceMenuTarget.WORK, work_id=i
                ).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=PlaceMenuCB(
                action=Action.BACK, target=PlaceMenuTarget.NONE, work_id=-1
            ).pack(),
        ),
    )
    return builder.as_markup()


async def send_place_menu(func, state: FSMContext, session: async_sessionmaker):
    await state.update_data(work_id=None)

    data = await state.get_data()

    cleaning = CleaningDTO.from_dict(data)
    place_id = await get_place_id(state)
    place = cleaning.places[place_id]
    await func(
        text=f"Место уборки: {escape_chars(place.name)}",
        reply_markup=get_place_keyboard(place),
    )
    await state.set_state(OperatorMenu.Cleaning.Place.menu)
