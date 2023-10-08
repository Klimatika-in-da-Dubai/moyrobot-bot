from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.dao.group import GroupDAO
from app.services.database.models.group import Group
from app.utils.group import get_selected_group_id
from app.utils.text import escape_chars


class SelectedGroupTarget(IntEnum):
    MAILING = auto()
    DELETE = auto()
    BACK = auto()


class SelectedGroupCB(CallbackData, prefix="selected_group"):
    action: Action
    target: SelectedGroupTarget


def get_selected_group_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Рассылки",
            callback_data=SelectedGroupCB(
                action=Action.OPEN, target=SelectedGroupTarget.MAILING
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Удалить группу",
            callback_data=SelectedGroupCB(
                action=Action.OPEN, target=SelectedGroupTarget.DELETE
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=SelectedGroupCB(
                action=Action.BACK, target=SelectedGroupTarget.BACK
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_selected_group_menu(func, state: FSMContext, session: AsyncSession):
    group_id = await get_selected_group_id(state)
    if group_id is None:
        raise ValueError("Error ")

    groupdao = GroupDAO(session)
    group = await groupdao.get_by_id(id_=group_id)
    if not isinstance(group, Group):
        raise TypeError("group is doesn't exists")

    await state.set_state(AdminMenu.Groups.Selected.menu)
    await func(
        text=f"Группа: {escape_chars(group.name)}",
        reply_markup=get_selected_group_menu_keyboard(),
    )
