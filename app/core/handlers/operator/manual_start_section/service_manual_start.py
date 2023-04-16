from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_report import (
    get_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import get_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.service_manual_start import (
    ServiceManualStartCB,
    ServiceManualStartTarget,
    get_service_manual_start_keyboard,
)

from app.core.states.operator import OperatorMenu
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import (
    ManualStartType,
    ServiceManualStart,
)


service_manual_start_router = Router()


@service_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.ServiceManualStart.menu,
    ServiceManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == ServiceManualStartTarget.DESCRIPTION)
    ),
)
async def cb_description(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(
        OperatorMenu.ManualStartSection.ServiceManualStart.description
    )
    await cb.message.answer("Напишите причну ручного запуска")  # type: ignore


@service_manual_start_router.message(
    OperatorMenu.ManualStartSection.ServiceManualStart.description, F.text
)
async def message_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OperatorMenu.ManualStartSection.ServiceManualStart.menu)
    await message.answer(
        "Технический запуск", reply_markup=get_service_manual_start_keyboard()
    )


@service_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.ServiceManualStart.menu,
    ServiceManualStartCB.filter((F.action == Action.BACK)),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(description="")
    await state.set_state(OperatorMenu.ManualStartSection.type)
    await cb.message.edit_text(  # type: ignore
        "Выберите тип ручного запуска", reply_markup=get_manual_start_type_keyboard()
    )


@service_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.ServiceManualStart.menu,
    ServiceManualStartCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    id = data.get("id")
    description = data.get("description")

    service_manual_start = ServiceManualStart(id=id, description=description)
    manual_start_dao = ManualStartDAO(session)

    await manual_start_dao.report_typed_manual_start(
        service_manual_start, ManualStartType.SERVICE
    )
    await state.clear()
    await state.set_state(OperatorMenu.ManualStartSection.menu)
    await cb.message.edit_text(  # type: ignore
        "Ручные запуски", reply_markup=await get_manual_starts_keyboard(session)
    )


def check_data(data) -> bool:
    id = data.get("id")
    description = data.get("description")

    if id is None:
        return False

    if description is None or description == "":
        return False

    return True
