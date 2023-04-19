from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dao.manual_start import ManualStartDAO

MANUAL_STARTS_KEYBOARD_COUNT = 5


class ManualStartSectionTarget(IntEnum):
    MANUAL_START = auto()
    NONE = auto()


class ManualStartSectionCB(CallbackData, prefix="omenu_man_start"):
    action: Action
    target: ManualStartSectionTarget
    manual_start_id: str


async def get_manual_starts_keyboard(
    session: async_sessionmaker[AsyncSession],
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    manual_start_dao = ManualStartDAO(session=session)
    manual_starts = await manual_start_dao.get_n_unreported_manual_starts(
        MANUAL_STARTS_KEYBOARD_COUNT
    )

    for manual_start in manual_starts:
        builder.row(
            types.InlineKeyboardButton(
                text=f"Терминал: {manual_start.terminal_id} Id: {manual_start.id}",
                callback_data=ManualStartSectionCB(
                    action=Action.OPEN,
                    target=ManualStartSectionTarget.MANUAL_START,
                    manual_start_id=manual_start.id,
                ).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ManualStartSectionCB(
                action=Action.BACK,
                target=ManualStartSectionTarget.NONE,
                manual_start_id="",
            ).pack(),
        ),
    )
    return builder.as_markup()


async def send_manual_starts_keyboard(
    send_func: Callable,
    state: FSMContext,
    session: async_sessionmaker,
):
    await state.set_state(OperatorMenu.ManualStartSection.menu)
    await send_func(
        "Ручные запуски", reply_markup=await get_manual_starts_keyboard(session)
    )
