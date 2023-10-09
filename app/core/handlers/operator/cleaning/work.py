from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.base import Action, CancelCB
from app.core.keyboards.operator.cleaning.cleaning import send_cleaning_menu
from app.core.keyboards.operator.cleaning.place import (
    send_place_menu,
)
from app.core.keyboards.operator.cleaning.work import WorkMenuCB, WorkMenuTarget

from app.core.states.operator import OperatorMenu
from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.dto.cleaning import CleaningDTO
from app.utils.cleaning import get_current_place, get_place_id, get_work_id
from PIL import Image
import imagehash

work_router = Router()


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.menu,
    isOperatorCB(),
    WorkMenuCB.filter(
        (F.action == Action.OPEN) & (F.target == WorkMenuTarget.CHANGE_PHOTO)
    ),
)
@work_router.message(OperatorMenu.Cleaning.Place.Work.photo, F.photo)
async def message_work_photo(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    data = await state.get_data()
    cleaning = CleaningDTO.from_dict(data)
    place_id = await get_place_id(state)
    work_id = await get_work_id(state)
    work = cleaning.places[place_id].works[work_id]
    photo = message.photo[-1]  # type: ignore
    photo_hash = await get_image_hash(bot, photo)

    if await CleaningDAO(session).photo_hash_already_exists(photo_hash):
        await message.answer(
            "Дубликат\\! Вы не должны использовать одно фото в разных уборках \\:\\)"
        )
        return

    work.photo_file_id = photo.file_id  # type: ignore
    work.photo_hash = photo_hash
    await state.update_data(cleaning=cleaning.to_dict())

    place = await get_current_place(state)
    if place.is_filled():
        await send_cleaning_menu(message.answer, state, session)
        return
    await send_place_menu(message.answer, state, session)


async def get_image_hash(bot: Bot, photo: types.PhotoSize) -> str:
    result = await bot.download(photo.file_id)
    image = Image.open(result)  # type: ignore
    return str(imagehash.average_hash(image))


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.photo,
    isOperatorCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
    F.message.text,
)
async def cb_cancel(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await cb.answer()
    await send_place_menu(cb.message.edit_text, state, session)  # type: ignore


@work_router.callback_query(
    OperatorMenu.Cleaning.Place.Work.photo,
    isOperatorCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
    F.message.photo,
)
async def cb_cancel_with_photo(
    cb: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await cb.answer()
    await cb.message.delete()  # type: ignore
    await send_place_menu(cb.message.answer, state, session)  # type: ignore
