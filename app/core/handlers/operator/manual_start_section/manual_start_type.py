from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_report import (
    ManualStartReportCB,
    ManualStartReportTarget,
)
from app.core.keyboards.operator.manual_start.menu import get_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.paid_manual_start import (
    get_paid_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.rewash_manual_start import (
    get_rewash_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.service_manual_start import (
    get_service_manual_start_keyboard,
)
from app.core.keyboards.operator.manual_start.test_manual_start import (
    get_test_manual_start_keyboard,
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
async def cb_test_manual_start(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(type=ManualStartType.TEST)
    await state.set_state(OperatorMenu.ManualStartSection.TestManualStart.menu)
    await cb.message.edit_text(  # type: ignore
        "Тестовый запуск", reply_markup=get_test_manual_start_keyboard()
    )


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.SERVICE_MANUAL_START)
    ),
)
async def cb_service_manual_start(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(type=ManualStartType.SERVICE)
    await state.set_state(OperatorMenu.ManualStartSection.ServiceManualStart.menu)
    await cb.message.edit_text(  # type: ignore
        "Техничксий запуск", reply_markup=get_service_manual_start_keyboard()
    )


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.REWASH_MANUAL_START)
    ),
)
async def cb_rewash_manual_start(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(type=ManualStartType.REWASH)
    await state.set_state(OperatorMenu.ManualStartSection.RewashManualStart.menu)
    await cb.message.edit_text(  # type: ignore
        "Перемывка", reply_markup=get_rewash_manual_start_keyboard()
    )


@manual_start_type_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.type,
    ManualStartReportCB.filter(
        (F.action == Action.OPEN)
        & (F.target == ManualStartReportTarget.PAID_MANUAL_START)
    ),
)
async def cb_paid_manual_start(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(type=ManualStartType.PAID)
    await state.set_state(OperatorMenu.ManualStartSection.PaidManualStart.menu)
    await cb.message.edit_text(  # type: ignore
        "Оплата через эквайринг", reply_markup=get_paid_manual_start_keyboard()
    )


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
    await state.set_state(OperatorMenu.ManualStartSection.menu)
    await cb.message.edit_text(  # type: ignore
        "Ручные запуски", reply_markup=await get_manual_starts_keyboard(session)
    )
