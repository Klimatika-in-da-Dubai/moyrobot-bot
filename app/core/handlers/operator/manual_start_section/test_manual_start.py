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
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.dao.user import UserDAO
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

    id = data.get("id")
    description = data.get("description")

    test_manual_start = TestManualStart(id=id, description=description)
    manual_start_dao = ManualStartDAO(session)

    await manual_start_dao.report_typed_manual_start(
        test_manual_start, ManualStartType.TEST
    )
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def report_test_manual_start(
    bot: Bot, session: async_sessionmaker, test_manual_start_id: int
):
    userdao = UserDAO(session)
    manual_start_dao = ManualStartDAO(session)
    ids_to_report = await userdao.get_ids_to_report_test_manual_start()

    test_manual_start = await manual_start_dao.get_typed_manual_start(
        test_manual_start_id, ManualStartType.TEST
    )
    for id in ids_to_report:
        ...


def check_data(data) -> bool:
    id = data.get("id")
    description = data.get("description")

    if id is None:
        return False

    if description is None or description == "":
        return False

    return True
