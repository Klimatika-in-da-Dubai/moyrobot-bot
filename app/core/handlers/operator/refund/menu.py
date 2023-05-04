from aiogram import Router, types, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.refund.base import RefundMenuCB, RefundMenuTarget
from app.core.keyboards.operator.refund.menu import send_refund_keyboard

from app.core.states.operator import OperatorMenu
from app.services.database.dao.refund import RefundDAO
from app.services.database.models.refund import PaymentDevice
from app.services.database.models.utils import PaymentMethod
from app.utils.refund import check_refund_report, get_refund


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == RefundMenuTarget.PAYMENT_DEVICE)
    ),
)
async def cb_payment_device(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()

    refund = await get_refund(state)

    match refund.payment_device:
        case PaymentDevice.CASHBOX:
            await state.update_data(payment_device=PaymentDevice.TERMINAL)
        case PaymentDevice.TERMINAL | None:
            await state.update_data(payment_device=PaymentDevice.CASHBOX)

    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == RefundMenuTarget.PAYMENT_METHOD)
    ),
)
async def cb_payment_method(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()

    refund = await get_refund(state)

    match refund.payment_method:
        case PaymentMethod.CASH:
            await state.update_data(payment_method=PaymentMethod.CARD)
        case PaymentMethod.CARD | None:
            await state.update_data(payment_method=PaymentMethod.CASH)

    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == RefundMenuTarget.DESCRIPTION)
    ),
)
async def cb_description(
    cb: types.CallbackQuery,
    state: FSMContext,
):
    await cb.answer()
    await state.set_state(OperatorMenu.Refund.description)
    await cb.message.edit_text(  # type: ignore
        "Напишите причину возврата", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Refund.description, F.text)
async def message_description(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    await state.update_data(description=message.text)
    await send_refund_keyboard(message.answer, state, session)


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == RefundMenuTarget.STATEMENT_PHOTO)
    ),
)
async def cb_statement_photo(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.Refund.statement_photo)

    refund = await get_refund(state)

    if refund.statement_photo_file_id is None:
        await cb.message.edit_text(  # type: ignore
            "Пришлите фото заявления", reply_markup=get_cancel_keyboard()
        )

        return
    await cb.message.delete()  # type: ignore
    await cb.message.answer_photo(  # type: ignore
        photo=refund.statement_photo_file_id,
        caption="Можете изменить фото заявления",
        reply_markup=get_cancel_keyboard(),
    )


@menu_router.message(OperatorMenu.Refund.statement_photo, F.photo)
async def message_statement_photo(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    await state.update_data(statement_photo_file_id=message.photo[-1].file_id)  # type: ignore
    await send_refund_keyboard(message.answer, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == RefundMenuTarget.CONSUMABLE_PHOTO)
    ),
)
async def cb_consumable_photo(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.Refund.consumable_photo)

    refund = await get_refund(state)

    if refund.consumable_photo_file_id is None:
        await cb.message.edit_text(  # type: ignore
            "Пришлите фото расходника", reply_markup=get_cancel_keyboard()
        )
        return

    await cb.message.delete()  # type: ignore
    await cb.message.answer_photo(  # type: ignore
        photo=refund.consumable_photo_file_id,
        caption="Можете изменить фото расходника",
        reply_markup=get_cancel_keyboard(),
    )


@menu_router.message(OperatorMenu.Refund.consumable_photo, F.photo)
async def message_consumable_photo(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    await state.update_data(consumable_photo_file_id=message.photo[-1].file_id)  # type: ignore
    await send_refund_keyboard(message.answer, state, session)


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == RefundMenuTarget.GIVE_MONEY)
    ),
)
async def cb_give_money(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    data = await state.get_data()
    await state.update_data(give_money=not data.get("give_money"))
    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter(
        (F.action == Action.SELECT) & (F.target == RefundMenuTarget.MONEY_ON_CARD)
    ),
)
async def cb_money_on_card(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    data = await state.get_data()
    await state.update_data(money_on_card=not data.get("money_on_card"))
    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    if not await check_refund_report(state):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    await cb.answer()
    refund = await get_refund(state)

    refund_dao = RefundDAO(session)
    await refund_dao.add_refund(refund)
    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Refund.menu,
    isOperatorCB(),
    RefundMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    or_f(
        OperatorMenu.Refund.consumable_photo,
        OperatorMenu.Refund.statement_photo,
        OperatorMenu.Refund.description,
    ),
    isOperatorCB(),
    CancelCB.filter(F.action == Action.CANCEL),
    F.message.text,
)
async def cb_cancel(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    or_f(
        OperatorMenu.Refund.consumable_photo,
        OperatorMenu.Refund.statement_photo,
    ),
    isOperatorCB(),
    CancelCB.filter(F.action == Action.CANCEL),
    F.message.photo,
)
async def cb_cancel_media(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await cb.message.delete()  # type: ignore
    await send_refund_keyboard(cb.message.answer, state, session)  # type: ignore
