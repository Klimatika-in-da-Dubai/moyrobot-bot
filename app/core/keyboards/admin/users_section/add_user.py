from enum import IntEnum, auto
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action
from app.services.database.models.user import Role


class AddUserTarget(IntEnum):
    NONE = auto()
    ID = auto()
    NAME = auto()
    ROLES = auto()
    OPERATOR_ROLE = auto()
    MODERATOR_ROLE = auto()
    ADMIN_ROLE = auto()


class AddUserCB(CallbackData, prefix="amenu_add_user"):
    action: Action
    target: AddUserTarget


async def get_add_user_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    id, name = await get_user_info_from_state(state)

    text_id = str(id) if id is not None else ""
    text_name = name if name is not None else ""

    builder.row(
        types.InlineKeyboardButton(
            text=f"Id: {text_id}",
            callback_data=AddUserCB(
                action=Action.ENTER_TEXT, target=AddUserTarget.ID
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Имя: {text_name}",
            callback_data=AddUserCB(
                action=Action.ENTER_TEXT, target=AddUserTarget.NAME
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Роли",
            callback_data=AddUserCB(
                action=Action.OPEN, target=AddUserTarget.ROLES
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=AddUserCB(
                action=Action.BACK, target=AddUserTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=AddUserCB(
                action=Action.ENTER, target=AddUserTarget.NONE
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
            callback_data=AddUserCB(
                action=Action.SELECT, target=AddUserTarget.OPERATOR_ROLE
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Модератор {mod_role_emoji_status}",
            callback_data=AddUserCB(
                action=Action.SELECT, target=AddUserTarget.MODERATOR_ROLE
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Админ {adm_role_emoji_status}",
            callback_data=AddUserCB(
                action=Action.SELECT, target=AddUserTarget.ADMIN_ROLE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=AddUserCB(
                action=Action.BACK, target=AddUserTarget.ROLES
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
