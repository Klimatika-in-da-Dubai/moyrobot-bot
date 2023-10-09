from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action
from app.core.keyboards.operator.manual_start.corporations import (
    CorporationsMenuCB,
    send_corporations_menu,
)
from app.core.keyboards.operator.manual_start.type import (
    send_manual_start_type_keyboard,
)
from app.core.keyboards.operator.manual_start.menu import (
    send_manual_starts_keyboard,
)
from app.core.keyboards.operator.manual_start.corporate import (
    CorporateManualStartCB,
    CorporateManualStartTarget,
    send_corporate_manual_start_keyboard,
)
from app.core.states.operator import OperatorMenu

from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import (
    ManualStartType,
    CorporateManualStart,
)


corporate_manual_start_router = Router()


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.menu,
    isOperatorCB(),
    CorporateManualStartCB.filter(
        (F.action == Action.ADD_PHOTO) & (F.target == CorporateManualStartTarget.PHOTO),
    ),
)
async def cb_photo(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.CorporateManualStart.photo)
    await cb.message.edit_text(  # type: ignore
        "Сделайте фотографию так, чтобы было хорошо видно номер автомобиля"
    )


@corporate_manual_start_router.message(
    OperatorMenu.ManualStart.CorporateManualStart.photo, F.photo
)
async def message_photo(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    photo_file_id = message.photo[-1].file_id  # type: ignore
    await state.update_data(photo_file_id=photo_file_id)
    await send_corporate_manual_start_keyboard(message.answer, state, session)


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.menu,
    isOperatorCB(),
    CorporateManualStartCB.filter(
        (F.action == Action.ENTER_TEXT)
        & (F.target == CorporateManualStartTarget.DESCRIPTION),
    ),
)
async def cb_description(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(OperatorMenu.ManualStart.CorporateManualStart.description)
    await cb.message.edit_text("Напишите причину перемывки")  # type: ignore


@corporate_manual_start_router.message(
    OperatorMenu.ManualStart.CorporateManualStart.description, F.text
)
async def message_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(description=message.text)
    await send_corporate_manual_start_keyboard(message.answer, state, session)


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.menu,
    isOperatorCB(),
    CorporateManualStartCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await state.update_data(photo_file_id=None, description=None)
    await send_manual_start_type_keyboard(cb.message.edit_text, state, session)  # type: ignore


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.menu,
    isOperatorCB(),
    CorporateManualStartCB.filter(
        (F.action == Action.OPEN) & (F.target == CorporateManualStartTarget.CORPORATION)
    ),
)
async def cb_open_corporation_menu(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_corporations_menu(cb.message.edit_text, state, session)  # type: ignore


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.corporation,
    isOperatorCB(),
    CorporationsMenuCB.filter((F.action == Action.SELECT)),
)
async def cb_select_corporation(
    cb: types.CallbackQuery,
    callback_data: CorporationsMenuCB,
    state: FSMContext,
    session: AsyncSession,
):
    await cb.answer()
    await state.update_data(corporation_id=callback_data.corporation_id)
    await send_corporate_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.corporation,
    isOperatorCB(),
    CorporationsMenuCB.filter(F.action == Action.BACK),
)
async def cb_corporations_menu_back(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await send_corporate_manual_start_keyboard(cb.message.edit_text, state, session)  # type: ignore


@corporate_manual_start_router.callback_query(
    OperatorMenu.ManualStart.CorporateManualStart.menu,
    isOperatorCB(),
    CorporateManualStartCB.filter(F.action == Action.ENTER),
)
async def cb_enter(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if not check_data(data):
        await cb.answer("Не все поля были заполнены", show_alert=True)
        return

    await table_add_corporate_manual_start(state, session)
    await state.clear()
    await send_manual_starts_keyboard(cb.message.edit_text, state, session)  # type: ignore


async def table_add_corporate_manual_start(state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    id = data.get("id")
    photo_file_id = data.get("photo_file_id")
    description = data.get("description")
    corporation_id = data.get("corporation_id")

    corporate_manual_start = CorporateManualStart(
        id=id,
        photo_file_id=photo_file_id,
        description=description,
        corporation_id=corporation_id,
    )
    manual_start_dao = ManualStartDAO(session)
    await manual_start_dao.report_typed_manual_start(
        corporate_manual_start, ManualStartType.CORPORATE
    )


def check_data(data):
    id = data.get("id")
    photo_file_id = data.get("photo_file_id")
    description = data.get("description")
    corporation_id = data.get("corporation_id")

    if id is None or id == "":
        return False

    if photo_file_id is None or photo_file_id == "":
        return False

    if description is None or description == "":
        return False

    if corporation_id is None:
        return False

    return True
