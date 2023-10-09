from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.utils.bonus import get_bonus_info, get_bonus_text


class BonusMenuTarget(IntEnum):
    NONE = auto()
    PHONE = auto()
    BONUS_AMOUNT = auto()
    DESCRIPTION = auto()


class BonusMenuCB(CallbackData, prefix="bonus"):
    action: Action
    target: BonusMenuTarget


async def get_bonus_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    phone_em, bonus_em, descripiton_em = await get_bonus_info_status_emoji(state)
    builder.row(
        types.InlineKeyboardButton(
            text=f"Номер телефона {phone_em}",
            callback_data=BonusMenuCB(
                action=Action.ENTER_TEXT, target=BonusMenuTarget.PHONE
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Количество бонусов {bonus_em}",
            callback_data=BonusMenuCB(
                action=Action.ENTER_TEXT, target=BonusMenuTarget.BONUS_AMOUNT
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Причина {descripiton_em}",
            callback_data=BonusMenuCB(
                action=Action.ENTER_TEXT, target=BonusMenuTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=BonusMenuCB(
                action=Action.BACK, target=BonusMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=BonusMenuCB(
                action=Action.ENTER, target=BonusMenuTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_bonus_info_status_emoji(state: FSMContext):
    phone, bonus_amount, description = await get_bonus_info(state)

    phone_em = "✅" if phone is not None else "❌"
    bonus_em = "✅" if bonus_amount is not None else "❌"
    description_em = "✅" if description is not None else "❌"

    return phone_em, bonus_em, description_em


async def send_bonus_keyboard(func, state: FSMContext, session: AsyncSession):
    text = await get_bonus_text(state)
    await state.set_state(OperatorMenu.Bonus.menu)
    await func(text=text, reply_markup=await get_bonus_keyboard(state))
