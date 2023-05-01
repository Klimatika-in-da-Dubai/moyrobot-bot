from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.keyboards.operator.shift.robot import (
    RobotCheckMenuCB,
    RobotCheckMenuTarget,
    send_robot_check_keyboard,
)

from app.core.states.operator import OperatorMenu
from app.utils.shift import get_open_shift


robot_check_router = Router()


@robot_check_router.callback_query(
    OperatorMenu.Shift.robot_check,
    isOperatorCB(),
    RobotCheckMenuCB.filter(F.action == Action.SELECT),
)
async def cb_select(
    cb: types.CallbackQuery,
    callback_data: RobotCheckMenuCB,
    state: FSMContext,
    session: async_sessionmaker,
):
    await cb.answer()
    shift = await get_open_shift(state)
    match callback_data.target:
        case RobotCheckMenuTarget.MOVEMENT:
            await state.update_data(robot_movement_check=not shift.robot_movement_check)
        case RobotCheckMenuTarget.LEAK:
            await state.update_data(robot_leak_check=not shift.robot_leak_check)
    await send_robot_check_keyboard(cb.message.edit_text, state, session)  # type: ignore


@robot_check_router.callback_query(
    OperatorMenu.Shift.robot_check,
    isOperatorCB(),
    RobotCheckMenuCB.filter(F.action == Action.ENTER),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, state, session)  # type: ignore
