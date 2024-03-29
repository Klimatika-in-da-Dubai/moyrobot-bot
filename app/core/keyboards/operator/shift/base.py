from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.shift import CloseShift, OpenShift


class ShiftMenuTarget(IntEnum):
    NONE = auto()
    OPERATOR_NAME = auto()
    MONEY_AMOUNT = auto()
    ANTIFREEZE_COUNT = auto()
    EQUIPMENT_CHECK = auto()
    CHEMISTRY = auto()
    ROBOT_CHECK = auto()
    GATES_CHECK = auto()
    COINS_CHECK = auto()
    NAPKINS_CHECK = auto()


class ShiftMenuCB(CallbackData, prefix="shift"):
    action: Action
    target: ShiftMenuTarget


@dataclass
class ShiftEmojis:
    operator_name: Literal["✅", "❌"]
    money_amount: Literal["✅", "❌"]
    antifreeze_count: Literal["✅", "❌"]
    equipment_check: Literal["✅", "❌"]
    robot_check: Literal["✅", "❌"]
    gates_check: Literal["✅", "❌"]
    coins_check: Literal["✅", "❌"]
    napkins_check: Literal["✅", "❌"]


@dataclass
class ShiftInfo:
    operator_name: str
    money_amount: str
    antifreeze_count: str
    equipment_check: bool
    robot_check: bool
    gates_check: bool
    coins_check: bool
    napkins_check: bool


def get_shift_menu_builder(
    shift: OpenShift | CloseShift, operator_name: str | None = None
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    shift_info = get_shift_menu_info(shift, operator_name)
    emojis: ShiftEmojis = get_shift_menu_emojis(shift, operator_name)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Оператор: {shift_info.operator_name} {emojis.operator_name}",
            callback_data=ShiftMenuCB(
                action=Action.OPEN, target=ShiftMenuTarget.OPERATOR_NAME
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Денег в кассе: {shift_info.money_amount} {emojis.money_amount}",
            callback_data=ShiftMenuCB(
                action=Action.ENTER_TEXT, target=ShiftMenuTarget.MONEY_AMOUNT
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Кол-во незамерзайки: {shift_info.antifreeze_count} {emojis.antifreeze_count}",
            callback_data=ShiftMenuCB(
                action=Action.ENTER_TEXT, target=ShiftMenuTarget.ANTIFREEZE_COUNT
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Осмотр оборудования {emojis.equipment_check}",
            callback_data=ShiftMenuCB(
                action=Action.SELECT, target=ShiftMenuTarget.EQUIPMENT_CHECK
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Химия",
            callback_data=ShiftMenuCB(
                action=Action.OPEN, target=ShiftMenuTarget.CHEMISTRY
            ).pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Исправность работы робота {emojis.robot_check}",
            callback_data=ShiftMenuCB(
                action=Action.OPEN, target=ShiftMenuTarget.ROBOT_CHECK
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Исправность работы ворот {emojis.gates_check}",
            callback_data=ShiftMenuCB(
                action=Action.SELECT, target=ShiftMenuTarget.GATES_CHECK
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Нужны монетки {emojis.coins_check}",
            callback_data=ShiftMenuCB(
                action=Action.SELECT, target=ShiftMenuTarget.COINS_CHECK
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Нужны салфетки {emojis.napkins_check}",
            callback_data=ShiftMenuCB(
                action=Action.SELECT, target=ShiftMenuTarget.NAPKINS_CHECK
            ).pack(),
        )
    )
    return builder


def get_shift_menu_info(shift: OpenShift | CloseShift, operator_name: str | None):
    operator_name = operator_name if operator_name is not None else ""
    money_amount = str(shift.money_amount) if shift.money_amount is not None else ""
    antifreeze_count = (
        str(shift.antifreeze_count) if shift.antifreeze_count is not None else ""
    )
    equipment_check = True if shift.equipment_check else False
    robot_check = (
        True if shift.robot_leak_check and shift.robot_movement_check else False
    )
    gates_check = True if shift.gates_check else False

    coins_check = True if shift.coins_check else False
    napkins_check = True if shift.napkins_check else False

    return ShiftInfo(
        operator_name=operator_name,
        money_amount=money_amount,
        antifreeze_count=antifreeze_count,
        equipment_check=equipment_check,
        robot_check=robot_check,
        gates_check=gates_check,
        coins_check=coins_check,
        napkins_check=napkins_check,
    )


def get_shift_menu_emojis(shift: OpenShift | CloseShift, operator_name: str | None):
    operator_name = "✅" if operator_name is not None else "❌"
    money_amount = "✅" if shift.money_amount is not None else "❌"
    antifreeze_count = "✅" if shift.antifreeze_count is not None else "❌"
    equipment_check = "✅" if shift.equipment_check else "❌"
    robot_check = "✅" if shift.robot_movement_check and shift.robot_leak_check else "❌"
    gates_check = "✅" if shift.gates_check else "❌"
    coins_check = "✅" if shift.coins_check else "❌"
    napkins_check = "✅" if shift.napkins_check else "❌"

    return ShiftEmojis(
        operator_name=operator_name,
        money_amount=money_amount,
        antifreeze_count=antifreeze_count,
        equipment_check=equipment_check,
        robot_check=robot_check,
        gates_check=gates_check,
        coins_check=coins_check,
        napkins_check=napkins_check,
    )
