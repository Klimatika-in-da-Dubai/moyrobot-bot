from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f


from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.antifreeze.menu import (
    AntifreezeMenuCB,
    AntifreezeMenuTarget,
    send_antifreeze_keyboard,
    send_payment_method_keyboard,
)
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.payment_method import PaymentMethodCB, PaymentMethodTarget
from app.core.states.operator import OperatorMenu
from app.services.database.dao.antifreeze import AntifreezeDAO
from app.services.database.models.antifreeze import Antifreeze, PaymentMethod
from app.utils.antifreeze import get_antifreeze_info


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Antifreeze.menu,
    isOperatorCB(),
    AntifreezeMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == AntifreezeMenuTarget.PAYMENT_METHOD)
    ),
)
async def cb_antifreeze_payment_method(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_payment_method_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Antifreeze.payment_method,
    isOperatorCB(),
    PaymentMethodCB.filter(F.action == Action.SELECT),
)
async def cb_payment_method_select(
    cb: types.CallbackQuery,
    callback_data: PaymentMethodCB,
    state: FSMContext,
    session: AsyncSession,
):
    payment_method_cb = callback_data.target

    match payment_method_cb:
        case PaymentMethodTarget.CARD:
            selected_method = PaymentMethod.CARD
        case PaymentMethodTarget.CASH:
            selected_method = PaymentMethod.CASH
        case _:
            raise ValueError("Error in payment method selection")

    await cb.answer()
    await state.update_data(payment_method=selected_method)
    await send_antifreeze_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Antifreeze.menu,
    isOperatorCB(),
    AntifreezeMenuCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == AntifreezeMenuTarget.PAYMENT_AMOUNT)
    ),
)
async def cb_antifreeze_payment_amount(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await state.set_state(OperatorMenu.Antifreeze.payment_amount)
    await cb.message.edit_text(  # type: ignore
        text="Напишите сумму оплаты в рублях", reply_markup=get_cancel_keyboard()
    )  # type: ignore


@menu_router.message(OperatorMenu.Antifreeze.payment_amount, F.text)
async def message_payment_amount(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if not message.text.isnumeric() or int(message.text) <= 0:  # type: ignore
        await message.answer("Не корректная сумма", reply_markup=get_cancel_keyboard())
        return

    await state.update_data(payment_amount=int(message.text))  # type: ignore
    await send_antifreeze_keyboard(message.answer, state, session)


@menu_router.callback_query(
    OperatorMenu.Antifreeze.menu,
    isOperatorCB(),
    AntifreezeMenuCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Antifreeze.menu,
    isOperatorCB(),
    AntifreezeMenuCB.filter(F.action == Action.ENTER),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    payment_method, payment_amount = await get_antifreeze_info(state)

    if any(el is None for el in (payment_method, payment_amount)):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    antifreezedao = AntifreezeDAO(session)
    antifreeze = Antifreeze(
        payment_method=payment_method, payment_amount=payment_amount
    )

    await antifreezedao.add_bonus(antifreeze)
    await clear_antifreeze_data(state)
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    or_f(
        OperatorMenu.Antifreeze.payment_amount,
    ),
    isOperatorCB(),
    CancelCB.filter(F.action == Action.CANCEL),
)
async def cb_cancel_enter_text(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_antifreeze_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def clear_antifreeze_data(state: FSMContext):
    await state.update_data(payment_method=None)
    await state.update_data(payment_amount=None)
