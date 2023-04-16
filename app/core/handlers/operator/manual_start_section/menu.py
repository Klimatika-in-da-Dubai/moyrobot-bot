from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.menu import (
    ManualStartSectionCB,
    ManualStartSectionTarget,
)
from app.core.keyboards.operator.menu import get_operator_menu_keyboard
from app.core.keyboards.operator.manual_start.manual_start_report import (
    get_manual_start_type_keyboard,
)
from app.core.states.operator import OperatorMenu

manual_start_menu_router = Router()


@manual_start_menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.menu,
    ManualStartSectionCB.filter(
        (F.action == Action.OPEN) & (F.target == ManualStartSectionTarget.MANUAL_START)
    ),
)
async def cb_manual_start_open(
    cb: types.CallbackQuery, state: FSMContext, callback_data: ManualStartSectionCB
):
    await cb.answer(text="В разработке", show_alert=True)
    await state.set_state(OperatorMenu.ManualStartSection.type)
    await state.update_data(id=callback_data.manual_start_id)
    await cb.message.edit_text(  # type: ignore
        text="Выберите тип ручного запуска",
        reply_markup=get_manual_start_type_keyboard(),
    )


@manual_start_menu_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.menu,
    ManualStartSectionCB.filter(
        F.action == Action.BACK & F.target == ManualStartSectionTarget.NONE
    ),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.menu)
    await cb.message.edit_text(  # type: ignore
        "Меню оператора", reply_markup=get_operator_menu_keyboard()
    )
