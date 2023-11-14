from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.keyboards.operator.promocode.menu import (
    PromocodeMenuCB,
    PromocodeMenuTarget,
    send_promocode_keyboard,
)
from app.core.keyboards.operator.promocode.mode import send_washmode_keyboard
from app.core.states.operator import OperatorMenu
from app.services.database.dao.promocode import PromocodeDAO
from app.services.database.models.promocode import Promocode
from app.utils.phone import is_phone_correct, phone_to_text
from app.utils.promocode import get_promocode_info


menu_router = Router()


@menu_router.callback_query(
    OperatorMenu.Promocode.menu,
    isOperatorCB(),
    PromocodeMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == PromocodeMenuTarget.PHONE)
    ),
)
async def cb_promocode_phone(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await state.set_state(OperatorMenu.Promocode.phone)
    await cb.message.edit_text(  # type: ignore
        "Введите номер телефона клиента", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Promocode.phone, F.text)
async def message_promocode_phone(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    phone = phone_to_text(message.text)  # type: ignore
    if not is_phone_correct(phone):
        await message.answer(
            "Некорректный номер телефона", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(phone=phone)
    await send_promocode_keyboard(message.answer, state, session)


@menu_router.callback_query(
    OperatorMenu.Promocode.menu,
    isOperatorCB(),
    PromocodeMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == PromocodeMenuTarget.WASH_MODE)
    ),
)
async def cb_promocode_wash_mode(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_washmode_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Promocode.menu,
    isOperatorCB(),
    PromocodeMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == PromocodeMenuTarget.DESCRIPTION)
    ),
)
async def cb_promocode_description(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await state.set_state(OperatorMenu.Promocode.description)
    await cb.message.edit_text(  # type: ignore
        "Напишите причину выдачи промокода", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Promocode.description, F.text)
async def message_promocode_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(promocode_description=message.text)
    await send_promocode_keyboard(message.answer, state, session)


@menu_router.callback_query(
    OperatorMenu.Promocode.menu,
    isOperatorCB(),
    PromocodeMenuCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.Promocode.menu,
    isOperatorCB(),
    PromocodeMenuCB.filter(F.action == Action.ENTER),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    phone, wash_mode, description = await get_promocode_info(state)

    if any(el is None for el in (phone, wash_mode, description)):
        await cb.answer(text="Не все поля заполенены", show_alert=True)
        return
    await cb.answer()

    promocodedao = PromocodeDAO(session=session)
    promocode = Promocode(phone=phone, wash_mode=wash_mode, description=description)
    await promocodedao.add_promocode(promocode)

    await clear_promocode_data(state)
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    or_f(OperatorMenu.Promocode.description, OperatorMenu.Promocode.phone),
    isOperatorCB(),
    CancelCB.filter(F.action == Action.CANCEL),
)
async def cb_cancel_enter_text(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_promocode_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def clear_promocode_data(state: FSMContext):
    await state.update_data(phone=None)
    await state.update_data(wash_mode=None)
    await state.update_data(promocode_description=None)
