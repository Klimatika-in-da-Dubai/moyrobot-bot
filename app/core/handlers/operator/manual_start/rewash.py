from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.handlers.operator.manual_start.utils import clear_manual_start_data
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import (
    send_manual_starts_keyboard,
)
from app.core.keyboards.operator.manual_start.rewash import (
    RewashManualStartCB,
    RewashManualStartTarget,
    send_rewash_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu

from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import ManualStartType, RewashManualStart


rewash_manual_start_router = Router()


@rewash_manual_start_router.callback_query(
    OperatorMenu.ManualStart.RewashManualStart.menu,
    isOperatorCB(),
    RewashManualStartCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == RewashManualStartTarget.PHOTO),
    ),
)
async def cb_photo(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.RewashManualStart.photo)
    await cb.message.edit_text(  # type: ignore
        "Сделайте фотографию так, чтобы было хорошо видно номер автомобиля"
    )


@rewash_manual_start_router.message(
    OperatorMenu.ManualStart.RewashManualStart.photo, F.photo
)
async def message_photo(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    photo_file_id = message.photo[-1].file_id  # type: ignore
    await state.update_data(photo_file_id=photo_file_id)
    await send_rewash_manual_start_keyboard(message.answer, state, session)


@rewash_manual_start_router.callback_query(
    OperatorMenu.ManualStart.RewashManualStart.menu,
    isOperatorCB(),
    RewashManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == RewashManualStartTarget.DESCRIPTION),
    ),
)
async def cb_description(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.RewashManualStart.description)
    await cb.message.edit_text("Напишите причину перемывки")  # type: ignore


@rewash_manual_start_router.message(
    OperatorMenu.ManualStart.RewashManualStart.description, F.text
)
async def message_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(description=message.text)
    await send_rewash_manual_start_keyboard(message.answer, state, session)


@rewash_manual_start_router.callback_query(
    OperatorMenu.ManualStart.RewashManualStart.menu,
    isOperatorCB(),
    RewashManualStartCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await state.update_data(photo_file_id=None, description=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@rewash_manual_start_router.callback_query(
    OperatorMenu.ManualStart.RewashManualStart.menu,
    isOperatorCB(),
    RewashManualStartCB.filter(F.action == Action.ENTER),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля были заполнены", show_alert=True)
        return

    await table_add_rewash_manual_start(state, session)

    await clear_manual_start_data(state)
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def table_add_rewash_manual_start(state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    id = data.get("id")
    photo_file_id = data.get("photo_file_id")
    description = data.get("description")
    rewash_manual_start = RewashManualStart(
        id=id, photo_file_id=photo_file_id, description=description
    )
    manual_start_dao = ManualStartDAO(session)
    await manual_start_dao.report_typed_manual_start(
        rewash_manual_start, ManualStartType.REWASH
    )


def check_data(data):
    id = data.get("id")
    photo_file_id = data.get("photo_file_id")
    description = data.get("description")

    if id is None or id == "":
        return False

    if photo_file_id is None or photo_file_id == "":
        return False

    if description is None or description == "":
        return False

    return True
