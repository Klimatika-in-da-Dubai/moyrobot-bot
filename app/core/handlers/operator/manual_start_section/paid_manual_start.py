from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, YesNoCB, YesNoTarget, get_yes_no_keyboard
from app.core.keyboards.operator.manual_start.manual_start_report import (
    get_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import get_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.paid_manual_start import (
    PaidManualStartCB,
    PaidManualStartTarget,
    PaymentMethodCB,
    PaymentMethodTarget,
    get_paid_manual_start_keyboard,
    get_payment_method_keyboard,
)
from app.core.states.operator import OperatorMenu
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import (
    ManualStartType,
    PaidManualStart,
    PaymentMethod,
)


paid_manual_start_router = Router()


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.menu,
    PaidManualStartCB.filter(
        (F.action == Action.OPEN) & (F.target == PaidManualStartTarget.PAYMENT_METHOD)
    ),
)
async def cb_payment_method(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(
        OperatorMenu.ManualStartSection.PaidManualStart.payment_method
    )
    await cb.message.edit_text(  # type: ignore
        "Выберите метод оплаты", reply_markup=await get_payment_method_keyboard(state)
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.payment_method,
    PaymentMethodCB.filter(F.action == Action.SELECT),
)
async def cb_payment_method_select(
    cb: types.CallbackQuery, callback_data: PaymentMethodCB, state: FSMContext
):
    payment_method_cb = callback_data.target
    selected_method = None
    match payment_method_cb:
        case PaymentMethodTarget.CARD:
            selected_method = PaymentMethod.CARD
        case PaymentMethodTarget.CASH:
            selected_method = PaymentMethod.CASH
        case _:
            raise ValueError("Error in payment method selection")

    await cb.answer()
    await state.update_data(payment_method=selected_method)
    await cb.message.edit_text(  # type: ignore
        "Выберите метод оплаты", reply_markup=await get_payment_method_keyboard(state)
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.payment_method,
    PaymentMethodCB.filter(F.action == Action.BACK),
)
async def cb_payment_method_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStartSection.PaidManualStart.menu)
    await cb.message.edit_text(  # type: ignore
        "Оплата через эквайринг", reply_markup=get_paid_manual_start_keyboard()
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.menu,
    PaidManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == PaidManualStartTarget.PAYMENT_AMOUNT)
    ),
)
async def cb_payment_amount(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(
        OperatorMenu.ManualStartSection.PaidManualStart.payment_amount
    )
    await cb.message.answer("Напишите сумму оплаты")  # type: ignore


@paid_manual_start_router.message(
    OperatorMenu.ManualStartSection.PaidManualStart.payment_amount, F.text
)
async def message_payment_amount(message: types.Message, state: FSMContext):
    payment_amount = message.text
    if not payment_amount.isnumeric():  # type: ignore
        await message.answer("Введите число")
        return
    await state.update_data(payment_amount=int(payment_amount))  # type: ignore
    await state.set_state(OperatorMenu.ManualStartSection.PaidManualStart.menu)
    await message.answer(
        "Оплата через эквайринг", reply_markup=get_paid_manual_start_keyboard()
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.menu,
    PaidManualStartCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(payment_method=None, payment_amount=None)
    await state.set_state(OperatorMenu.ManualStartSection.type)
    await cb.message.edit_text(  # type: ignore
        "Выберите тип ручного запуска", reply_markup=get_manual_start_type_keyboard()
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.menu,
    PaidManualStartCB.filter(F.action == Action.ENTER),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return
    id = data.get("id")
    payment_method = data.get("payment_method")
    payment_amount = data.get("payment_amount")

    paid_manual_start = PaidManualStart(
        id=id, payment_method=payment_method, payment_amount=payment_amount
    )
    manual_start_dao = ManualStartDAO(session)
    await manual_start_dao.report_typed_manual_start(
        paid_manual_start, ManualStartType.PAID
    )
    await state.clear()
    await state.set_state(OperatorMenu.ManualStartSection.PaidManualStart.bonus)
    await cb.message.edit_text(  # type: ignore
        "Хотите начислить бонусы?", reply_markup=get_yes_no_keyboard()
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.bonus,
    YesNoCB.filter((F.action == Action.SELECT) & (F.target == YesNoTarget.NO)),
)
async def cb_bonus_no(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStartSection.menu)
    await cb.message.edit_text(  # type: ignore
        "Ручные запуски", reply_markup=await get_manual_starts_keyboard(session)
    )


@paid_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.PaidManualStart.bonus,
    YesNoCB.filter((F.action == Action.SELECT) & (F.target == YesNoTarget.YES)),
)
async def cb_bonus_yes(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer("В разработке", show_alert=True)


def check_data(data) -> bool:
    id = data.get("id")
    payment_method = data.get("payment_method")
    payment_amount = data.get("payment_amount")

    if id is None or id == "":
        return False

    if payment_method is None:
        return False

    if payment_amount is None:
        return False

    return True