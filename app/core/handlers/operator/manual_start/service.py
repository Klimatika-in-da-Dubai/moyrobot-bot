import logging
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import send_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.service import (
    ServiceManualStartCB,
    ServiceManualStartTarget,
    send_service_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu

from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import (
    ManualStartType,
    ServiceManualStart,
)

service_manual_start_router = Router()


@service_manual_start_router.callback_query(
    OperatorMenu.ManualStart.ServiceManualStart.menu,
    isOperatorCB(),
    ServiceManualStartCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == ServiceManualStartTarget.PHOTO),
    ),
)
async def cb_photo(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.ServiceManualStart.photo)
    await cb.message.edit_text(  # type: ignore
        "Сделайте фотографию так, чтобы было хорошо видно номер автомобиля"
    )


@service_manual_start_router.message(
    OperatorMenu.ManualStart.ServiceManualStart.photo, F.photo
)
async def message_photo(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    photo_file_id = message.photo[-1].file_id  # type: ignore
    await state.update_data(photo_file_id=photo_file_id)
    await send_service_manual_start_keyboard(message.answer, state, session)


@service_manual_start_router.callback_query(
    OperatorMenu.ManualStart.ServiceManualStart.menu,
    isOperatorCB(),
    ServiceManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == ServiceManualStartTarget.DESCRIPTION)
    ),
)
async def cb_description(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.ServiceManualStart.description)
    await cb.message.edit_text("Напишите причну ручного запуска")  # type: ignore


@service_manual_start_router.message(
    OperatorMenu.ManualStart.ServiceManualStart.description, F.text
)
async def message_description(message: types.Message, state: FSMContext, session):
    await state.update_data(description=message.text)
    await send_service_manual_start_keyboard(message.answer, state, session)


@service_manual_start_router.callback_query(
    OperatorMenu.ManualStart.ServiceManualStart.menu,
    isOperatorCB(),
    ServiceManualStartCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(description=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@service_manual_start_router.callback_query(
    OperatorMenu.ManualStart.ServiceManualStart.menu,
    isOperatorCB(),
    ServiceManualStartCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker, bot: Bot
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    await table_add_service_manual_start(state, session)
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def table_add_service_manual_start(
    state: FSMContext, session: async_sessionmaker
):
    data = await state.get_data()
    id = data.get("id")
    description = data.get("description")
    photo_file_id = data.get("photo_file_id")
    service_manual_start = ServiceManualStart(
        id=id, description=description, photo_file_id=photo_file_id
    )
    manual_start_dao = ManualStartDAO(session)

    await manual_start_dao.report_typed_manual_start(
        service_manual_start, ManualStartType.SERVICE
    )


def check_data(data) -> bool:
    id = data.get("id")
    description = data.get("description")
    photo_file_id = data.get("photo_file_id")

    if id is None:
        return False

    if description is None or description == "":
        return False

    if photo_file_id is None:
        return False

    return True
