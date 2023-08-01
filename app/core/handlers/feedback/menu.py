from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from app.core.middlewares.media_group import MediaGroupMiddleware

from app.core.states.feedback import FeedbackMenu


feedback_menu_router = Router()
feedback_menu_router.message.middleware(MediaGroupMiddleware())


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.html_text.is_(""))
async def feedback_no_text(message: Message):
    await message.answer("Вы должны указать сообщениe")


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.media_group_id)
async def get_feedback_media(message: Message, state: FSMContext, album: list[Message]):
    if len(album) > 10:
        await message.answer("Вы прикрепили слишком много фото (Максмум 10)")
        return

    await message.answer(message.html_text)


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.photo)
async def get_feedback_photo(message: Message, state: FSMContext):
    await message.answer("Get photo")


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.text)
async def get_feedback(message: Message, state: FSMContext):
    await message.answer("Get text")


async def create_feedback(message: Message, photos: list[PhotoSize] | None = None):
    ...
