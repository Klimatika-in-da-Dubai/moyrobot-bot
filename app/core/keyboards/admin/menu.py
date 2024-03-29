from enum import IntEnum, auto
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu


class AdminMenuTarget(IntEnum):
    NONE = auto()
    MONEY_COLLECTION = auto()
    CASHBOX_REPLENISHMENT = auto()
    USER = auto()
    GROUP = auto()


class AdminMenuCB(CallbackData, prefix="admin_menu"):
    action: Action
    target: AdminMenuTarget


def get_admin_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Пользователи",
            callback_data=AdminMenuCB(
                action=Action.OPEN, target=AdminMenuTarget.USER
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Группы",
            callback_data=AdminMenuCB(
                action=Action.OPEN, target=AdminMenuTarget.GROUP
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Пополнение кассы",
            callback_data=AdminMenuCB(
                action=Action.ENTER_TEXT, target=AdminMenuTarget.CASHBOX_REPLENISHMENT
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Инкассация",
            callback_data=AdminMenuCB(
                action=Action.ENTER_TEXT, target=AdminMenuTarget.MONEY_COLLECTION
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=AdminMenuCB(
                action=Action.BACK, target=AdminMenuTarget.NONE
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_admin_menu(func, state: FSMContext):
    await state.set_state(AdminMenu.menu)
    await func(text="Админ меню", reply_markup=get_admin_menu_keyboard())
