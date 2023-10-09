from typing import assert_never
from aiogram import F, Router, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.shift.chemistry import (
    ChemistryMenuCB,
    ChemistryMenuTarget,
    send_chemistry_menu,
)
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.states.operator import OperatorMenu
from app.utils.shift import get_open_shift

chemistry_router = Router()


@chemistry_router.callback_query(
    OperatorMenu.Shift.Chemistry.menu,
    ChemistryMenuCB.filter((F.action == Action.INPUT)),
)
async def cb_chemistry_input(
    cb: CallbackQuery,
    callback_data: ChemistryMenuCB,
    state: FSMContext,
):
    await cb.answer()

    match callback_data.target:
        case ChemistryMenuTarget.SHAMPOO:
            new_state = OperatorMenu.Shift.Chemistry.shampoo
            text = "Введите количество оставшегося шампуня"
        case ChemistryMenuTarget.FOAM:
            new_state = OperatorMenu.Shift.Chemistry.foam
            text = "Введите количество оставшейся пены"
        case ChemistryMenuTarget.WAX:
            new_state = OperatorMenu.Shift.Chemistry.wax
            text = "Введите количество оставшегося воска"
        case _ as never:
            assert_never(never)
    await state.set_state(new_state)
    await cb.message.edit_text(text=text, reply_markup=get_cancel_keyboard())  # type: ignore


@chemistry_router.message(OperatorMenu.Shift.Chemistry.shampoo, F.text)
async def message_shampoo_count(
    message: types.Message,
    state: FSMContext,
):
    if not message.text.isnumeric() or int(message.text) < 0:  # type: ignore
        await message.answer(
            "Неверное количество шампнуя", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(shampoo_count=int(message.text))  # type: ignore
    await send_chemistry_menu(message.answer, state)


@chemistry_router.message(OperatorMenu.Shift.Chemistry.foam, F.text)
async def message_foam_count(
    message: types.Message,
    state: FSMContext,
):
    if not message.text.isnumeric() or int(message.text) < 0:  # type: ignore
        await message.answer(
            "Неверное количество пены", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(foam_count=int(message.text))  # type: ignore
    await send_chemistry_menu(message.answer, state)


@chemistry_router.message(OperatorMenu.Shift.Chemistry.wax, F.text)
async def message_wax_count(
    message: types.Message,
    state: FSMContext,
):
    if not message.text.isnumeric() or int(message.text) < 0:  # type: ignore
        await message.answer(
            "Неверное количество воска", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(wax_count=int(message.text))  # type: ignore
    await send_chemistry_menu(message.answer, state)


@chemistry_router.callback_query(
    or_f(
        OperatorMenu.Shift.Chemistry.shampoo,
        OperatorMenu.Shift.Chemistry.foam,
        OperatorMenu.Shift.Chemistry.wax,
    ),
    CancelCB.filter(),
)
async def cb_input_cancel(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_chemistry_menu(cb.message.edit_text, state)  # type: ignore


@chemistry_router.callback_query(
    OperatorMenu.Shift.Chemistry.menu,
    ChemistryMenuCB.filter(F.action == Action.SELECT),
)
async def cb_chemistry_check(
    cb: CallbackQuery,
    callback_data: ChemistryMenuCB,
    state: FSMContext,
):
    await cb.answer()
    shift = await get_open_shift(state)
    match callback_data.target:
        case ChemistryMenuTarget.SHAMPOO:
            await state.update_data(shampoo_check=not shift.shampoo_check)
        case ChemistryMenuTarget.FOAM:
            await state.update_data(foam_check=not shift.foam_check)
        case ChemistryMenuTarget.WAX:
            await state.update_data(wax_check=not shift.wax_check)
        case _ as never:
            assert_never(never)
    await send_chemistry_menu(cb.message.edit_text, state)  # type: ignore


@chemistry_router.callback_query(
    OperatorMenu.Shift.Chemistry.menu,
    isOperatorCB(),
    ChemistryMenuCB.filter(F.action == Action.ENTER),
)
async def cb_chemistry_enter(
    cb: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
