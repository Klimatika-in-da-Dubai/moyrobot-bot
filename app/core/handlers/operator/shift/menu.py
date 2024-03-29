from aiogram import F, Router, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.shift.base import (
    ShiftMenuCB,
    ShiftMenuTarget,
)
from app.core.keyboards.operator.shift.chemistry import (
    send_chemistry_menu,
)
from app.core.keyboards.operator.shift.close import (
    CloseShiftMenuCB,
)
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.keyboards.operator.shift.open import (
    OpenShiftMenuCB,
)
from app.core.keyboards.operator.shift.operator import send_operators_keyboard
from app.core.keyboards.operator.shift.robot import send_robot_check_keyboard
from app.core.states.operator import OperatorMenu
from app.services.database.dao.user import UserDAO
from app.utils.shift import get_open_shift


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == ShiftMenuTarget.OPERATOR_NAME)
    ),
)
async def cb_operator_name(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    userdao = UserDAO(session)
    if not await userdao.is_work_account(cb.message.chat.id):  # type: ignore
        await cb.answer("Вы не можете сменить оператора.", show_alert=True)
        return
    await cb.answer()
    await send_operators_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == ShiftMenuTarget.MONEY_AMOUNT)
    ),
)
async def cb_money_amount(
    cb: types.CallbackQuery,
    state: FSMContext,
):
    await cb.answer()
    await state.set_state(OperatorMenu.Shift.money_amount)
    await cb.message.edit_text(  # type: ignore
        "Напишите количество денег в кассе", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Shift.money_amount, F.text)
async def message_money_amount(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if not message.text.isnumeric() or int(message.text) < 0:  # type: ignore
        await message.answer(
            "Неверное количество денег в кассе", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(money_amount=int(message.text))  # type: ignore
    await send_shift_keyboard(message.answer, message, state, session)


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == ShiftMenuTarget.ANTIFREEZE_COUNT)
    ),
)
async def cb_antifreeze_count(
    cb: types.CallbackQuery,
    state: FSMContext,
):
    await cb.answer()
    await state.set_state(OperatorMenu.Shift.antifreeze_count)
    await cb.message.edit_text(  # type: ignore
        "Напишите количество незмерзайки", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Shift.antifreeze_count, F.text)
async def message_antifreeze_count(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if not message.text.isnumeric() or int(message.text) < 0:  # type: ignore
        await message.answer(
            "Неверное количество незамерзайки", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(antifreeze_count=int(message.text))  # type: ignore
    await send_shift_keyboard(message.answer, message, state, session)


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == ShiftMenuTarget.EQUIPMENT_CHECK)
    ),
)
async def cb_equipment_check(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    shift = await get_open_shift(state)
    await state.update_data(equipment_check=not shift.equipment_check)
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == ShiftMenuTarget.CHEMISTRY)
    ),
)
async def cb_chemistry_count(
    cb: types.CallbackQuery,
    state: FSMContext,
):
    await cb.answer()

    if cb.message is None:
        raise ValueError("test")

    await send_chemistry_menu(cb.message.edit_text, state)


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == ShiftMenuTarget.ROBOT_CHECK)
    ),
)
async def cb_robot_check(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_robot_check_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == ShiftMenuTarget.GATES_CHECK)
    ),
)
async def cb_gates_check(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    shift = await get_open_shift(state)
    await state.update_data(gates_check=not shift.gates_check)
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == ShiftMenuTarget.COINS_CHECK)
    ),
)
async def cb_coins_check(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    shift = await get_open_shift(state)
    await state.update_data(coins_check=not shift.coins_check)
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    ShiftMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == ShiftMenuTarget.NAPKINS_CHECK)
    ),
)
async def cb_napkins_check(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    shift = await get_open_shift(state)
    await state.update_data(napkins_check=not shift.napkins_check)
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Shift.menu,
    isOperatorCB(),
    or_f(
        OpenShiftMenuCB.filter(F.action == Action.BACK),
        CloseShiftMenuCB.filter(F.action == Action.BACK),
    ),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    or_f(
        OperatorMenu.Shift.money_amount,
        OperatorMenu.Shift.antifreeze_count,
    ),
    isOperatorCB(),
    CancelCB.filter(F.action == Action.CANCEL),
)
async def cb_cancel(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
