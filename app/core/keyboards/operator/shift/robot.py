from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.models.shift import CloseShift, OpenShift
from app.utils.shift import get_open_shift


class RobotCheckMenuTarget(IntEnum):
    NONE = auto()
    MOVEMENT = auto()
    LEAK = auto()


class RobotCheckMenuCB(CallbackData, prefix="robot_check"):
    action: Action
    target: RobotCheckMenuTarget


@dataclass
class RobotCheckEmojis:
    movement_check: Literal["✅", "❌"]
    leak_check: Literal["✅", "❌"]


@dataclass
class RobotCheckInfo:
    movement_check: bool
    leak_check: bool


def get_robot_check_keyboard(shift: OpenShift | CloseShift):
    builder = InlineKeyboardBuilder()

    robot_check_info = get_robot_check_info(shift)
    emojis: RobotCheckEmojis = get_robot_check_emojis(robot_check_info)
    builder.row(
        types.InlineKeyboardButton(
            text=f"Ходит ровно? {emojis.movement_check}",
            callback_data=RobotCheckMenuCB(
                action=Action.SELECT, target=RobotCheckMenuTarget.MOVEMENT
            ).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=f"Протечек нет? {emojis.leak_check}",
            callback_data=RobotCheckMenuCB(
                action=Action.SELECT, target=RobotCheckMenuTarget.LEAK
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=RobotCheckMenuCB(
                action=Action.ENTER, target=RobotCheckMenuTarget.NONE
            ).pack(),
        ),
    )
    return builder.as_markup()


def get_robot_check_info(shift: OpenShift | CloseShift) -> RobotCheckInfo:
    movement_check = True if shift.robot_movement_check else False
    leak_check = True if shift.robot_leak_check else False

    return RobotCheckInfo(movement_check=movement_check, leak_check=leak_check)


def get_robot_check_emojis(robot_check_info: RobotCheckInfo) -> RobotCheckEmojis:
    movement_check_em = "✅" if robot_check_info.movement_check else "❌"
    leak_check_em = "✅" if robot_check_info.leak_check else "❌"
    return RobotCheckEmojis(movement_check=movement_check_em, leak_check=leak_check_em)


async def send_robot_check_keyboard(
    func, state: FSMContext, session: async_sessionmaker
):
    await state.set_state(OperatorMenu.Shift.robot_check)
    shift = await get_open_shift(state)
    await func(
        text="Исправность работы робота", reply_markup=get_robot_check_keyboard(shift)
    )
