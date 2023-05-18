from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.filters.shift import isShiftClosedCB, isShiftOpenedCB
from app.core.keyboards.base import Action
from app.core.keyboards.menu import send_menu_keyboard
from app.core.keyboards.operator.antifreeze.menu import send_antifreeze_keyboard
from app.core.keyboards.operator.bonus.menu import send_bonus_keyboard
from app.core.keyboards.operator.cleaning.cleaning import send_cleaning_menu
from app.core.keyboards.operator.manual_start.menu import (
    send_manual_starts_keyboard,
)
from app.core.keyboards.operator.menu import (
    OperatorMenuCB,
    OperatorMenuTarget,
)
from app.core.keyboards.operator.promocode.menu import send_promocode_keyboard
from app.core.keyboards.operator.refund.menu import send_refund_keyboard
from app.core.keyboards.operator.shift.menu import send_shift_keyboard
from app.core.states.operator import OperatorMenu
from app.services.database.dto.cleaning import CleaningDTO, Place, Work

menu_router = Router(name="operator-menu-router")


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.OPEN_SHIFT)
    ),
    isShiftClosedCB(),
)
async def cb_open_shift(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.CLOSE_SHIFT)
    ),
    isShiftOpenedCB(),
)
async def cb_close_shift(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_shift_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.MANUAL_START)
    ),
)
async def cb_manual_start_open(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.CLEANING)
    ),
)
async def cb_cleaning_open(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    cleaning = CleaningDTO(
        places=[
            Place(
                name="Бокс 1",
                works=[
                    Work(name="По направлению движения"),
                    Work(name="Против направления движения"),
                ],
            ),
            Place(
                name="Бокс 2",
                works=[
                    Work(name="По направлению движения"),
                    Work(name="Против направления движения"),
                ],
            ),
            Place(name="Территория 1", works=[Work(name="Территория у ворот")]),
            Place(
                name="Территория 2",
                works=[Work(name="Пылесос"), Work(name="Мойка ковров")],
            ),
            Place(
                name="Операторская",
                works=[Work(name="Общее фото помещения"), Work(name="Фото стола")],
            ),
            Place(
                name="Техническое помещение",
                works=[
                    Work(name="Шкаф доз 1"),
                    Work(name="Шкаф доз 2"),
                    Work(name="Общее фото"),
                ],
            ),
        ]
    )
    await state.update_data(cleaning=cleaning.to_dict())
    await send_cleaning_menu(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.PROMOCODE)
    ),
)
async def cb_promocode(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_promocode_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.BONUS)
    ),
)
async def cb_bonus(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_bonus_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.REFUND)
    ),
)
async def cb_refund(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await send_refund_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == OperatorMenuTarget.ANTIFREEZE)
    ),
)
async def cb_antifreeze(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_antifreeze_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    OperatorMenu.menu,
    isOperatorCB(),
    OperatorMenuCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    await cb.answer()
    await send_menu_keyboard(cb.message.edit_text, cb.message, state, session)  # type: ignore
