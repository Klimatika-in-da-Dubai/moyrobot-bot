from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.menu import send_menu_keyboard
from app.core.middlewares.media_group import MediaGroupMiddleware

from app.core.states.feedback import FeedbackMenu
from app.services.database.dao.feedback import FeedbackDAO
from app.services.database.models.feedback import Feedback


feedback_menu_router = Router()
feedback_menu_router.message.middleware(MediaGroupMiddleware())


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.html_text.is_(""))
async def feedback_no_text(message: Message):
    await message.answer("Вы должны указать сообщениe")


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.media_group_id)
async def get_feedback_media(
    message: Message,
    state: FSMContext,
    session: async_sessionmaker,
    album: list[Message],
):
    if len(album) > 10:
        await message.answer("Вы прикрепили слишком много фото (Максимум 10)")
        return

    photos = [mes.photo[-1] for mes in album]  # pyright: ignore
    text = message.html_text

    await create_feedback(message.chat.id, session, text, photos)

    await exit_get_feedback(message, state, session)


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.photo)
async def get_feedback_photo(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    photos = [message.photo[-1]]  # pyright: ignore
    text = message.html_text
    await create_feedback(message.chat.id, session, text, photos)

    await exit_get_feedback(message, state, session)


@feedback_menu_router.message(FeedbackMenu.get_feedback, F.text)
async def get_feedback(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    text = message.html_text
    await create_feedback(message.chat.id, session, text)

    await exit_get_feedback(message, state, session)


async def create_feedback(
    from_user_id: int,
    session: async_sessionmaker,
    text: str,
    photos: list[PhotoSize] | None = None,
):
    if photos is None:
        photos = []

    feedback = Feedback(from_user_id=from_user_id, text=text, photos=photos)
    feedbackdao = FeedbackDAO(session)
    await feedbackdao.add_feedback(feedback)


async def exit_get_feedback(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    await send_menu_keyboard(message.answer, message, state, session)
