from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.manual_start_type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import send_manual_starts_keyboard
from app.core.keyboards.operator.manual_start.test_manual_start import (
    TestManualStartCB,
    TestManualStartTarget,
    send_test_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu
from app.services.database.dao.mailing import MailingDAO
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import ManualStartType, TestManualStart

test_manual_start_router = Router()


@test_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.TestManualStart.menu,
    TestManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == TestManualStartTarget.DESCRIPTION)
    ),
)
async def cb_description(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStartSection.TestManualStart.description)
    await cb.message.answer("Напишите причну ручного запуска")  # type: ignore


@test_manual_start_router.message(
    OperatorMenu.ManualStartSection.TestManualStart.description, F.text
)
async def message_description(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    await state.update_data(description=message.text)
    await send_test_manual_start_keyboard(message.answer, state, session)


@test_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.TestManualStart.menu,
    TestManualStartCB.filter((F.action == Action.BACK)),
)
async def cb_back(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
):
    await cb.answer()
    await state.update_data(description=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@test_manual_start_router.callback_query(
    isOperatorCB(),
    OperatorMenu.ManualStartSection.TestManualStart.menu,
    TestManualStartCB.filter((F.action == Action.ENTER)),
)
async def cb_enter(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker, bot: Bot
):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля заполнены", show_alert=True)
        return

    id: str = data.get("id")  # type: ignore
    await table_add_test_manual_start(state, session)
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore
    await report_test_manual_start(bot, session, id)


async def table_add_test_manual_start(state: FSMContext, session: async_sessionmaker):
    data = await state.get_data()
    id = data.get("id")
    description = data.get("description")

    test_manual_start = TestManualStart(id=id, description=description)
    manual_start_dao = ManualStartDAO(session)

    await manual_start_dao.report_typed_manual_start(
        test_manual_start, ManualStartType.TEST
    )


async def report_test_manual_start(
    bot: Bot, session: async_sessionmaker, test_manual_start_id: str
):
    mailingdao = MailingDAO(session)
    manual_start_dao = ManualStartDAO(session)

    test_manual_start: TestManualStart = await manual_start_dao.get_typed_manual_start(
        test_manual_start_id, ManualStartType.TEST
    )

    text = (
        "Получен отчёт о ручном запуске\n"
        "\n"
        "Ручной запуск:\n"
        "*Тип:* Тест\n"
        f"*ID:* {test_manual_start.id}\n"
        f"*Причина:* {test_manual_start.description}"
    )

    ids = await mailingdao.get_mailing_ids(MailingType.MANUAL_START)
    for id in ids:
        await bot.send_message(id, text=text)


def check_data(data) -> bool:
    id = data.get("id")
    description = data.get("description")

    if id is None:
        return False

    if description is None or description == "":
        return False

    return True
