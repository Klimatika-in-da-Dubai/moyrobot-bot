from enum import IntEnum, auto
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.keyboards.payment_method import get_payment_method_keyboard
from app.core.states.operator import OperatorMenu
from app.utils.antifreeze import get_antifreeze_info, get_antifreeze_text


class AntifreezeMenuTarget(IntEnum):
    NONE = auto()
    PAYMENT_METHOD = auto()
    PAYMENT_AMOUNT = auto()


class AntifreezeMenuCB(CallbackData, prefix="antifreeze"):
    action: Action
    target: AntifreezeMenuTarget


async def get_antifreeze_keyboard(state: FSMContext) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    payment_method_em, payment_amount_em = await get_antifreeze_info_status_emoji(state)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Способ оплаты {payment_method_em}",
            callback_data=AntifreezeMenuCB(
                action=Action.OPEN, target=AntifreezeMenuTarget.PAYMENT_METHOD
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Сумма оплаты {payment_amount_em}",
            callback_data=AntifreezeMenuCB(
                action=Action.ENTER_TEXT, target=AntifreezeMenuTarget.PAYMENT_AMOUNT
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=AntifreezeMenuCB(
                action=Action.BACK, target=AntifreezeMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=AntifreezeMenuCB(
                action=Action.ENTER, target=AntifreezeMenuTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_antifreeze_info_status_emoji(state: FSMContext):
    payment_method, payment_amount = await get_antifreeze_info(state)

    payment_method_em = "✅" if payment_method is not None else "❌"
    payment_amount_em = "✅" if payment_amount is not None else "❌"

    return payment_method_em, payment_amount_em


async def send_antifreeze_keyboard(
    func, state: FSMContext, session: async_sessionmaker
):
    text = await get_antifreeze_text(state)

    await state.set_state(OperatorMenu.Antifreeze.menu)
    await func(text=text, reply_markup=await get_antifreeze_keyboard(state))


async def send_payment_method_keyboard(
    func, state: FSMContext, session: async_sessionmaker
):
    await state.set_state(OperatorMenu.Antifreeze.payment_method)
    await func(
        text="Выбирите способ оплаты",
        reply_markup=await get_payment_method_keyboard(state),
    )
