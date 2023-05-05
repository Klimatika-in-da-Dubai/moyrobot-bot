from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.refund import PaymentDevice, Refund
from app.services.database.models.utils import PaymentMethod


class RefundMenuTarget(IntEnum):
    PAYMENT_DEVICE = auto()
    PAYMENT_METHOD = auto()
    DESCRIPTION = auto()
    STATEMENT_PHOTO = auto()
    CONSUMABLE_PHOTO = auto()
    GIVE_MONEY = auto()
    MONEY_ON_CARD = auto()
    NONE = auto()


class RefundMenuCB(CallbackData, prefix="refund"):
    action: Action
    target: RefundMenuTarget


@dataclass
class RefundText:
    payment_device: str
    payment_method: str


@dataclass
class RefundEmojis:
    payment_device: Literal["✅", "❌"]
    payment_method: Literal["✅", "❌"]
    description: Literal["✅", "❌"]
    statement_photo: Literal["✅", "❌"]
    consumable_photo: Literal["✅", "❌"]
    give_money: Literal["✅", "❌"]
    money_on_card: Literal["✅", "❌"]


async def get_refund_base_builder(
    refund: Refund, state: FSMContext
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    refund_text: RefundText = get_refund_menu_text(refund)
    emojis: RefundEmojis = await get_refund_emojis(refund, state)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Оплата через: {refund_text.payment_device} {emojis.payment_device}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.PAYMENT_DEVICE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Способ оплаты: {refund_text.payment_method} {emojis.payment_method}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.PAYMENT_METHOD
            ).pack(),
        )
    )
    return builder


def get_refund_menu_text(refund: Refund) -> RefundText:
    payment_device = PaymentDevice.get_name(refund.payment_device)
    payment_method = PaymentMethod.get_name(refund.payment_method)

    return RefundText(payment_device=payment_device, payment_method=payment_method)


async def get_refund_emojis(refund: Refund, state: FSMContext) -> RefundEmojis:
    data = await state.get_data()

    payment_device = "✅" if refund.payment_device is not None else "❌"
    payment_method = "✅" if refund.payment_method is not None else "❌"
    description = "✅" if refund.description is not None else "❌"
    statement_photo = "✅" if refund.statement_photo_file_id is not None else "❌"
    consumable_photo = "✅" if refund.consumable_photo_file_id is not None else "❌"
    give_money = "✅" if data.get("give_money") else "❌"
    money_on_card = "✅" if data.get("money_on_card") else "❌"

    return RefundEmojis(
        payment_device=payment_device,
        payment_method=payment_method,
        description=description,
        statement_photo=statement_photo,
        consumable_photo=consumable_photo,
        give_money=give_money,
        money_on_card=money_on_card,
    )
