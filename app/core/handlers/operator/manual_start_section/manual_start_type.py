from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_type import (
    ManualStartReportCB,
    ManualStartReportTarget,
)
from app.core.keyboards.operator.manual_start.menu import send_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.paid_manual_start import (
    send_paid_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.rewash_manual_start import (
    send_rewash_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.service_manual_start import (
    send_service_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.test_manual_start import (
    send_test_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu
from app.services.database.models.manual_start import ManualStartType

manual_start_type_router = Router()


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.TEST_MANUAL_START)
    ),
)
async def cb_test_manual_start(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(type=ManualStartType.TEST)
    await state.set_state(OperatorMenu.ManualStartSection.TestManualStart.menu)
    await send_test_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.SERVICE_MANUAL_START)
    ),
)
async def cb_service_manual_start(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(type=ManualStartType.SERVICE)
    await send_service_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.REWASH_MANUAL_START)
    ),
)
async def cb_rewash_manual_start(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(type=ManualStartType.REWASH)

    await send_rewash_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.PAID_MANUAL_START)
    ),
)
async def cb_paid_manual_start(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(type=ManualStartType.PAID)

    await send_paid_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore
