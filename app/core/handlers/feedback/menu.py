from operator import or_
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.message_len import MessageLenght
from app.core.keyboards.menu import send_menu_keyboard
from app.core.middlewares.media_group import MediaGroupMiddleware

from app.core.states.feedback import FeedbackMenu
from app.services.database.dao.feedback import FeedbackDAO
from app.services.database.models.feedback import Feedback


feedback_menu_router = Router()
feedback_menu_router.message.middleware(MediaGroupMiddleware())


@feedback_menu_router.message(
    FeedbackMenu.get_feedback,
    F.media_group_id,
    F.caption,
    MessageLenght(max_length=950),
)
async def get_feedback_media(
    message: Message,
    state: FSMContext,
    session: async_sessionmaker,
    album: list[Message],
):
    photos = [mes.photo[-1] for mes in album]  # pyright: ignore

    await create_feedback(message, session, photos)

    await exit_get_feedback(message, state, session)


@feedback_menu_router.message(
    FeedbackMenu.get_feedback, F.photo, F.caption, MessageLenght(max_length=950)
)
async def get_feedback_photo(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    photos = [message.photo[-1]]  # pyright: ignore
    await create_feedback(message, session, photos)

    await exit_get_feedback(message, state, session)


@feedback_menu_router.message(
    FeedbackMenu.get_feedback, F.text, MessageLenght(max_length=950)
)
async def get_feedback(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    await create_feedback(message, session)

    await exit_get_feedback(message, state, session)


@feedback_menu_router.message(FeedbackMenu.get_feedback)
async def feedback_no_text(message: Message):
    await message.answer("Вы должны указать сообщениe")


async def create_feedback(
    message: Message,
    session: async_sessionmaker,
    photos: list[PhotoSize] | None = None,
):
    if photos is None:
        photos = []

    photos_file_ids: list[str] = [photo.file_id for photo in photos]
    feedback = Feedback(
        from_user_id=message.chat.id,
        message_id=message.message_id,
        md_text=message.md_text,
        photos=photos_file_ids,
    )
    feedbackdao = FeedbackDAO(session)
    await feedbackdao.add_feedback(feedback)


async def exit_get_feedback(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    await message.answer(
        "Ваше сообщение будет передано администраторам",
        reply_to_message_id=message.message_id,
    )
    await send_menu_keyboard(message.answer, message, state, session)
