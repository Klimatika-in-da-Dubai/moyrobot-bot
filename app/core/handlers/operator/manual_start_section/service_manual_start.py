import logging
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import send_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.service_manual_start import (
    ServiceManualStartCB,
    ServiceManualStartTarget,
    send_service_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu
from app.services.database.dao.mailing import (
    get_mailing_ids,
)
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
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
async def message_description(message: types.Message, state: FSMContext, session):
    await state.update_data(description=message.text)
    await send_service_manual_start_keyboard(message.answer, state, session)


@service_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.ServiceManualStart.menu,
    ServiceManualStartCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(description=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@service_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.ServiceManualStart.menu,
    ServiceManualStartCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker, bot: Bot
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    id = data.get("id")  # type: ignore
    await table_add_service_manual_start(state, session)
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore
    await report_service_manual_start(bot, session, id)  # type: ignore


async def table_add_service_manual_start(
    state: FSMContext, session: async_sessionmaker
):
    data = await state.get_data()
    id = data.get("id")
    description = data.get("description")

    service_manual_start = ServiceManualStart(id=id, description=description)
    manual_start_dao = ManualStartDAO(session)

    await manual_start_dao.report_typed_manual_start(
        service_manual_start, ManualStartType.SERVICE
    )


async def report_service_manual_start(
    bot: Bot, session: async_sessionmaker, test_manual_start_id: str
):
    manual_start_dao = ManualStartDAO(session)

    service_manual_start: ServiceManualStart = (
        await manual_start_dao.get_typed_manual_start(
            test_manual_start_id, ManualStartType.SERVICE
        )
    )

    text = (
        "Получен отчёт о ручном запуске\n"
        "\n"
        "Ручной запуск:\n"
        "*Тип:* Технический\n"
        f"*ID:* {service_manual_start.id}\n"
        f"*Причина:* {service_manual_start.description}"
    )

    ids = await get_mailing_ids(session, MailingType.MANUAL_START)
    for id in ids:
        try:
            await bot.send_message(id, text=text)
        except Exception:
            logging.error("Can't send report to chat with id %s", id)


def check_data(data) -> bool:
    id = data.get("id")
    description = data.get("description")

    if id is None:
        return False

    if description is None or description == "":
        return False

    return True
