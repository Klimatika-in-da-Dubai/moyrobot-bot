from enum import IntEnum, auto
from typing import Callable
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.keyboards.payment_method import get_payment_method_keyboard
from app.core.states.operator import OperatorMenu
from app.services.database.models.manual_start import PaymentMethod
from app.utils.text import escape_chars


class PaidManualStartTarget(IntEnum):
    PAYMENT_METHOD = auto()
    PAYMENT_AMOUNT = auto()
    NONE = auto()


class PaidManualStartCB(CallbackData, prefix="service_mstart"):
    action: Action
    target: PaidManualStartTarget


def get_paid_manual_start_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Метод оплаты",
            callback_data=PaidManualStartCB(
                action=Action.OPEN,
                target=PaidManualStartTarget.PAYMENT_METHOD,
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Сумма оплаты",
            callback_data=PaidManualStartCB(
                action=Action.ENTER_TEXT,
                target=PaidManualStartTarget.PAYMENT_AMOUNT,
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=PaidManualStartCB(
                action=Action.BACK,
                target=PaidManualStartTarget.NONE,
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=PaidManualStartCB(
                action=Action.ENTER,
                target=PaidManualStartTarget.NONE,
            ).pack(),
        ),
    )
    return builder.as_markup()


async def get_manual_start_text(state: FSMContext):
    data = await state.get_data()

    id = escape_chars(data.get("id"))
    payment_method = data.get("payment_method")
    payment_amount = data.get("payment_amount")

    payment_method_text = ""
    if payment_method == PaymentMethod.CARD:
        payment_method_text = "Карта"
    elif payment_method == PaymentMethod.CASH:
        payment_method_text = "Наличные"

    payment_amount_text = payment_amount if payment_amount is not None else ""

    return (
        "Ручной запуск\n"
        "*Тип:* Оплата через эквайринг\n"
        f"*ID:* {id}\n"
        f"*Способ оплаты:* {payment_method_text}\n"
        f"*Сумма оплаты:* {payment_amount_text}\n"
    )


async def send_paid_manual_start_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    text = await get_manual_start_text(state)
    await state.set_state(OperatorMenu.ManualStart.PaidManualStart.menu)
    await send_func(text=text, reply_markup=get_paid_manual_start_keyboard())


async def send_payment_method_keyboard(
    send_func: Callable, state: FSMContext, session: async_sessionmaker
):
    await state.set_state(OperatorMenu.ManualStart.PaidManualStart.payment_method)
    await send_func(
        text="Выберите тип оплаты",
        reply_markup=await get_payment_method_keyboard(state),
    )
