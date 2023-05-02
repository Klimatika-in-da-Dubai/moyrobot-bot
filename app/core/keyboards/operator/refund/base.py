from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action


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


def get_refund_base_builder(refund: Refund) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    refund_text: RefundText = get_refund_text(refund)
    emojis: RefundEmojis = get_refund_emojis(refund)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Устройство: {refund_text.payment_device} {emojis.payment_device}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.PAYMENT_DEVICE
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Способ: {refund.payment_method} {emojis.payment_method}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.PAYMENT_METHOD
            ).pack(),
        )
    )
    return builder


def get_refund_text(refund: Refund) -> RefundText:
    payment_device = refund.payment_device if refund.payment_device is not None else ""
    payment_method
