from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.utils.cleaning import get_current_work


class WorkMenuTarget(IntEnum):
    NONE = auto()
    CHANGE_PHOTO = auto()


class WorkMenuCB(CallbackData, prefix="work"):
    action: Action
    target: WorkMenuTarget


def get_work_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=WorkMenuCB(
                action=Action.BACK, target=WorkMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Изменить",
            callback_data=WorkMenuCB(
                action=Action.ADD_PHOTO, target=WorkMenuTarget.CHANGE_PHOTO
            ).pack(),
        ),
    )
    return builder.as_markup()


async def send_work_menu(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    work = await get_current_work(state)
    await cb.message.answer_photo(  # type: ignore
        photo=work.photo_file_id,
        caption=f"Уборка: {work.name}",
        reply_markup=get_work_keyboard(),
    )
    await state.set_state(OperatorMenu.Cleaning.Place.Work.menu)
