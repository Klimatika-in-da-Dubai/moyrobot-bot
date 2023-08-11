from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.job import Iterable
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.dao.group import GroupDAO
from app.services.database.models.group import Group
from app.utils.group import unselect_group


class GroupsMenuCB(CallbackData, prefix="groupsmenu"):
    action: Action
    group_id: int


def get_groups_menu(groups: Iterable[Group]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.row(
            InlineKeyboardButton(
                text=group.name,
                callback_data=GroupsMenuCB(
                    action=Action.OPEN, group_id=group.id
                ).pack(),
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=GroupsMenuCB(action=Action.BACK, group_id=-1).pack(),
        )
    )
    return builder.as_markup()


async def send_groups_menu(func, state: FSMContext, session: async_sessionmaker):
    groupdao = GroupDAO(session)
    groups = await groupdao.get_all()

    await unselect_group(state)

    await state.set_state(AdminMenu.Groups.menu)
    await func(text="Чаты", reply_markup=get_groups_menu(groups))
