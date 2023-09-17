from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.core.keyboards.base import Action
from app.core.keyboards.utils import EditMessageFunc, SendMessageFunc
from app.core.states.operator import OperatorMenu

from app.services.database.models.shift import CloseShift, OpenShift
from app.utils.shift import get_open_shift


@dataclass
class ChemistryEmojis:
    shampoo_count: Literal["✅", "❌"]
    foam_count: Literal["✅", "❌"]
    wax_count: Literal["✅", "❌"]
    shampoo_check: Literal["✅", "❌"]
    foam_check: Literal["✅", "❌"]
    wax_check: Literal["✅", "❌"]


@dataclass
class ChemistryCount:
    shampoo_count: int
    foam_count: int
    wax_count: int


class ChemistryMenuTarget(IntEnum):
    SHAMPOO = auto()
    FOAM = auto()
    WAX = auto()


class ChemistryMenuCB(CallbackData, prefix="chemistry_menu"):
    action: Action
    target: ChemistryMenuTarget


def get_chemistry_keyboard(shift: OpenShift | CloseShift) -> InlineKeyboardMarkup:
    emojis = get_chemistry_emojis(shift)
    counts = get_chemistry_count(shift)
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=f"Кол-во шампуня: {counts.shampoo_count} {emojis.shampoo_count}",
            callback_data=ChemistryMenuCB(
                action=Action.INPUT, target=ChemistryMenuTarget.SHAMPOO
            ).pack(),
        ),
        InlineKeyboardButton(
            text=f"Нужно больше? {emojis.shampoo_check}",
            callback_data=ChemistryMenuCB(
                action=Action.SELECT, target=ChemistryMenuTarget.SHAMPOO
            ).pack(),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text=f"Кол-во пены: {counts.foam_count} {emojis.foam_count}",
            callback_data=ChemistryMenuCB(
                action=Action.INPUT, target=ChemistryMenuTarget.FOAM
            ).pack(),
        ),
        InlineKeyboardButton(
            text=f"Нужно больше? {emojis.foam_check}",
            callback_data=ChemistryMenuCB(
                action=Action.SELECT, target=ChemistryMenuTarget.FOAM
            ).pack(),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text=f"Кол-во воска: {counts.wax_count} {emojis.wax_count}",
            callback_data=ChemistryMenuCB(
                action=Action.INPUT, target=ChemistryMenuTarget.WAX
            ).pack(),
        ),
        InlineKeyboardButton(
            text=f"Нужно больше? {emojis.wax_check}",
            callback_data=ChemistryMenuCB(
                action=Action.SELECT, target=ChemistryMenuTarget.WAX
            ).pack(),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Готово",
            callback_data=ChemistryMenuCB(
                action=Action.ENTER, target=ChemistryMenuTarget.WAX
            ).pack(),
        ),
    )

    return builder.as_markup()


def get_chemistry_count(shift: OpenShift | CloseShift) -> ChemistryCount:
    return ChemistryCount(
        shampoo_count=value_to_int(shift.shampoo_count),
        foam_count=value_to_int(shift.foam_count),
        wax_count=value_to_int(shift.wax_count),
    )


def value_to_int(value: int | None) -> int:
    return value if value else 0


def get_chemistry_emojis(shift: OpenShift | CloseShift) -> ChemistryEmojis:
    return ChemistryEmojis(
        shampoo_count=value_to_emoji(shift.shampoo_count),
        foam_count=value_to_emoji(shift.foam_count),
        wax_count=value_to_emoji(shift.wax_count),
        shampoo_check=value_to_emoji(shift.shampoo_check),
        foam_check=value_to_emoji(shift.foam_check),
        wax_check=value_to_emoji(shift.wax_check),
    )


def value_to_emoji(value: int | bool) -> Literal["✅", "❌"]:
    return "✅" if value else "❌"


async def send_chemistry_menu(
    func: EditMessageFunc | SendMessageFunc,
    state: FSMContext,
) -> Message | bool:
    shift = await get_open_shift(state)

    await state.set_state(OperatorMenu.Shift.Chemistry.menu)
    return await func(
        text="Заполните поля химии", reply_markup=get_chemistry_keyboard(shift)
    )
