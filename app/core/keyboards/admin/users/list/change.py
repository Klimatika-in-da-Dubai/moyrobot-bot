from enum import IntEnum, auto
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.admin.users.list.menu import send_users_list_menu
from app.core.keyboards.base import Action
from app.services.database.dao.mailing import MailingDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import Role

from app.core.states.admin import AdminMenu
from app.utils.list import get_selected_user


class ChangeUserTarget(IntEnum):
    NONE = auto()
    ID = auto()
    NAME = auto()
    SALARY = auto()
    MAILING = auto()
    ROLES = auto()
    OPERATOR_ROLE = auto()
    MODERATOR_ROLE = auto()
    ADMIN_ROLE = auto()


class ChangeUserCB(CallbackData, prefix="amenu_add_user"):
    action: Action
    target: ChangeUserTarget


async def get_change_user_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    id, name = await get_user_info_from_state(state)

    text_id = str(id) if id is not None else ""
    text_name = name if name is not None else ""

    builder.row(
        types.InlineKeyboardButton(
            text=f"Id: {text_id}",
            callback_data=ChangeUserCB(
                action=Action.ENTER_TEXT, target=ChangeUserTarget.ID
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Имя: {text_name}",
            callback_data=ChangeUserCB(
                action=Action.ENTER_TEXT, target=ChangeUserTarget.NAME
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Зарплата",
            callback_data=ChangeUserCB(
                action=Action.ENTER_TEXT, target=ChangeUserTarget.SALARY
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Рассылки",
            callback_data=ChangeUserCB(
                action=Action.OPEN, target=ChangeUserTarget.MAILING
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Роли",
            callback_data=ChangeUserCB(
                action=Action.OPEN, target=ChangeUserTarget.ROLES
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ChangeUserCB(
                action=Action.BACK, target=ChangeUserTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=ChangeUserCB(
                action=Action.ENTER, target=ChangeUserTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_roles_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    user_roles = await get_user_roles_from_state(state)

    op_role_emoji_status = "✅" if Role.OPERATOR in user_roles else "❌"
    mod_role_emoji_status = "✅" if Role.MODERATOR in user_roles else "❌"
    adm_role_emoji_status = "✅" if Role.ADMIN in user_roles else "❌"

    builder.row(
        types.InlineKeyboardButton(
            text=f"Оператор {op_role_emoji_status}",
            callback_data=ChangeUserCB(
                action=Action.SELECT, target=ChangeUserTarget.OPERATOR_ROLE
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Модератор {mod_role_emoji_status}",
            callback_data=ChangeUserCB(
                action=Action.SELECT, target=ChangeUserTarget.MODERATOR_ROLE
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Админ {adm_role_emoji_status}",
            callback_data=ChangeUserCB(
                action=Action.SELECT, target=ChangeUserTarget.ADMIN_ROLE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ChangeUserCB(
                action=Action.BACK, target=ChangeUserTarget.ROLES
            ).pack(),
        ),
    )

    return builder.as_markup()


async def get_user_info_from_state(
    state: FSMContext,
) -> tuple[int, str]:
    data = await state.get_data()
    id: int = data.get("id")  # type: ignore
    name: str = data.get("name")  # type: ignore
    return id, name


async def get_user_roles_from_state(state: FSMContext) -> list[Role]:
    data = await state.get_data()
    roles = data.get("roles")
    if roles is None:
        return []
    return roles


async def send_change_user_menu(func, state: FSMContext):
    await state.set_state(AdminMenu.Users.List.Selected.Change.menu)
    await func(
        "Изменить пользователя",
        reply_markup=await get_change_user_keyboard(state),
    )
