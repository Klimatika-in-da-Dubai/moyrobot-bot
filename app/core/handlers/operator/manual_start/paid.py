import logging
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, YesNoCB, YesNoTarget, get_yes_no_keyboard
from app.core.keyboards.operator.bonus.menu import send_bonus_keyboard
from app.core.keyboards.operator.manual_start.type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import (
    send_manual_starts_keyboard,
)
from app.core.keyboards.operator.manual_start.paid import (
    PaidManualStartCB,
    PaidManualStartTarget,
    send_paid_manual_start_keyboard,
    send_payment_method_keyboard,
)
from app.core.keyboards.payment_method import PaymentMethodCB, PaymentMethodTarget
from app.core.states.operator import OperatorMenu
from app.services.database.dao.mailing import (
    get_mailing_ids,
)
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import (
    ManualStartType,
    PaidManualStart,
    PaymentMethod,
)

paid_manual_start_router = Router()


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.menu,
    isOperatorCB(),
    PaidManualStartCB.filter(
        (F.action == Action.OPEN) & (F.target == PaidManualStartTarget.PAYMENT_METHOD)
    ),
)
async def cb_payment_method(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_payment_method_keyboard(cb.message.edit_text, state, session)  # type: ignore


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.payment_method,
    isOperatorCB(),
    PaymentMethodCB.filter(F.action == Action.SELECT),
)
async def cb_payment_method_select(
    cb: types.CallbackQuery,
    callback_data: PaymentMethodCB,
    state: FSMContext,
    session: async_sessionmaker,
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
    await send_payment_method_keyboard(cb.message.edit_text, state, session)  # type: ignore


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.payment_method,
    isOperatorCB(),
    PaymentMethodCB.filter(F.action == Action.BACK),
)
async def cb_payment_method_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_paid_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.menu,
    isOperatorCB(),
    PaidManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == PaidManualStartTarget.PAYMENT_AMOUNT)
    ),
)
async def cb_payment_amount(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.PaidManualStart.payment_amount)
    await cb.message.edit_text("Напишите сумму оплаты")  # type: ignore


@paid_manual_start_router.message(
    OperatorMenu.ManualStart.PaidManualStart.payment_amount, F.text
)
async def message_payment_amount(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    payment_amount = message.text
    if not payment_amount.isnumeric() or int(message.text) <= 0:  # type: ignore
        await message.edit_text("Введите число")
        return
    await state.update_data(payment_amount=int(payment_amount))  # type: ignore

    await send_paid_manual_start_keyboard(message.answer, state, session)


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.menu,
    isOperatorCB(),
    PaidManualStartCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(payment_method=None, payment_amount=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.menu,
    isOperatorCB(),
    PaidManualStartCB.filter(F.action == Action.ENTER),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker, bot: Bot
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return
    id = data.get("id")

    await table_add_paid_manual_start(state, session)
    await state.clear()
    await report_paid_manual_start(bot, session, id)  # type: ignore

    await state.set_state(OperatorMenu.ManualStart.PaidManualStart.bonus)
    await cb.message.edit_text(  # type: ignore
        "Хотите начислить бонусы?", reply_markup=get_yes_no_keyboard()
    )


async def table_add_paid_manual_start(state: FSMContext, session: async_sessionmaker):
    data = await state.get_data()
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


async def report_paid_manual_start(
    bot: Bot, session: async_sessionmaker, test_manual_start_id: str
):
    manual_start_dao = ManualStartDAO(session)

    paid_manual_start: PaidManualStart = await manual_start_dao.get_typed_manual_start(
        test_manual_start_id, ManualStartType.PAID
    )
    payment_method_text = (
        "Карта"
        if paid_manual_start.payment_method == PaymentMethod.CARD
        else "Наличные"
    )

    text = (
        "Получен отчёт о ручном запуске\n"
        "\n"
        "Ручной запуск:\n"
        "*Тип:* Оплата через эквайринг\n"
        f"*ID:* {paid_manual_start.id}\n"
        f"*Тип оплаты:* {payment_method_text}\n"
        f"*Сумма оплаты:* {paid_manual_start.payment_amount}"
    )

    ids = await get_mailing_ids(session, MailingType.MANUAL_START)
    for id in ids:
        try:
            await bot.send_message(id, text=text)
        except Exception:
            logging.error("Can't send report to chat with id %s", id)


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.bonus,
    isOperatorCB(),
    YesNoCB.filter((F.action == Action.SELECT) & (F.target == YesNoTarget.NO)),
)
async def cb_bonus_no(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


@paid_manual_start_router.callback_query(
    OperatorMenu.ManualStart.PaidManualStart.bonus,
    isOperatorCB(),
    YesNoCB.filter((F.action == Action.SELECT) & (F.target == YesNoTarget.YES)),
)
async def cb_bonus_yes(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await send_bonus_keyboard(cb.message.edit_text, state, session)  # type: ignore


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
