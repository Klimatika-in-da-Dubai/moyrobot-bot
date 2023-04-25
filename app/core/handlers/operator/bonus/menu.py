from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard
from app.core.keyboards.operator.bonus.menu import (
    BonusMenuCB,
    BonusMenuTarget,
    send_bonus_keyboard,
)
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.states.operator import OperatorMenu
from app.utils.text import convert_text_to_phone, is_correct_phone


menu_router = Router()


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.Bonus.menu,
    BonusMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == BonusMenuTarget.PHONE)
    ),
)
async def cb_bonus_phone(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.set_state(OperatorMenu.Bonus.phone)
    await cb.message.edit_text(  # type: ignore
        "Введите номер телефона", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Bonus.phone, F.text)
async def message_phone(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    phone = convert_text_to_phone(message.text)  # type: ignore
    if not is_correct_phone(phone):
        await message.answer(
            "Некорректный номер телефона", reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(phone=phone)
    await send_bonus_keyboard(message.answer, state, session)


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.Bonus.menu,
    BonusMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == BonusMenuTarget.BONUS_AMOUNT)
    ),
)
async def cb_bonus_amount(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.set_state(OperatorMenu.Bonus.bonus_amount)
    await cb.message.edit_text(  # type: ignore
        "Введите количество бонусов", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Bonus.bonus_amount, F.text)
async def message_bonus_amount(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    if not message.text.isnumeric():  # type: ignore
        await message.answer(
            "Введена некорректная сумма", reply_markup=get_cancel_keyboard()
        )

    await state.update_data(bonus_amount=int(message.text))  # type: ignore
    await send_bonus_keyboard(message.answer, state, session)


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.Bonus.menu,
    BonusMenuCB.filter(
        (F.action == Action.ENTER_TEXT) & (F.target == BonusMenuTarget.DESCRIPTION)
    ),
)
async def cb_bonus_description(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.set_state(OperatorMenu.Bonus.description)
    await cb.message.edit_text(  # type: ignore
        "Напишите причину ручного запуска", reply_markup=get_cancel_keyboard()
    )


@menu_router.message(OperatorMenu.Bonus.description, F.text)
async def message_bonus_description(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    await state.update_data(description=message.text)
    await send_bonus_keyboard(message.answer, state, session)


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.Bonus.menu,
    BonusMenuCB.filter(F.action == Action.BACK),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.clear()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.Bonus.menu,
    BonusMenuCB.filter(F.action == Action.ENTER),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    ...


@menu_router.callback_query(
    isOperatorCB(),
    or_f(
        OperatorMenu.Bonus.phone,
        OperatorMenu.Bonus.bonus_amount,
        OperatorMenu.Bonus.description,
    ),
    CancelCB.filter(F.action == Action.CANCEL),
)
async def cb_cancel_enter_text(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_bonus_keyboard(cb.message.edit_text, state, session)  # type: ignore
