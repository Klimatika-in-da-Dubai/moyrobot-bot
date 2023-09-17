from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.message_len import MessageLenght
from app.core.keyboards.menu import send_menu_keyboard
from app.core.middlewares.media_group import MediaGroupMiddleware

from app.core.states.operator_request import OperatorRequestMenu
from app.services.database.dao.operator_request import OperatorRequestDAO
from app.services.database.models.operator_request import OperatorRequest


operator_request_menu_router = Router()
operator_request_menu_router.message.middleware(MediaGroupMiddleware())


@operator_request_menu_router.message(
    OperatorRequestMenu.get_operator_request,
    F.media_group_id,
    F.caption,
    MessageLenght(max_length=950),
)
async def get_operator_request_media(
    message: Message,
    state: FSMContext,
    session: async_sessionmaker,
    album: list[Message],
):
    photos = [mes.photo[-1] for mes in album]  # pyright: ignore

    await create_operator_request(message, session, photos)

    await exit_get_operator_request(message, state, session)


@operator_request_menu_router.message(
    OperatorRequestMenu.get_operator_request,
    F.photo,
    F.caption,
    MessageLenght(max_length=950),
)
async def get_operator_request_photo(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    photos = [message.photo[-1]]  # pyright: ignore
    await create_operator_request(message, session, photos)

    await exit_get_operator_request(message, state, session)


@operator_request_menu_router.message(
    OperatorRequestMenu.get_operator_request, F.text, MessageLenght(max_length=950)
)
async def get_operator_request(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    await create_operator_request(message, session)

    await exit_get_operator_request(message, state, session)


@operator_request_menu_router.message(OperatorRequestMenu.get_operator_request)
async def operator_request_no_text(message: Message):
    await message.answer("Вы должны указать сообщениe")


async def create_operator_request(
    message: Message,
    session: async_sessionmaker,
    photos: list[PhotoSize] | None = None,
):
    if photos is None:
        photos = []

    photos_file_ids: list[str] = [photo.file_id for photo in photos]
    operator_request = OperatorRequest(
        from_user_id=message.chat.id,
        message_id=message.message_id,
        md_text=message.md_text,
        photos=photos_file_ids,
    )
    operator_request_dao = OperatorRequestDAO(session)
    await operator_request_dao.add_operator_request(operator_request)


async def exit_get_operator_request(
    message: Message, state: FSMContext, session: async_sessionmaker
):
    await message.answer(
        "Ваше сообщение будет передано администраторам",
        reply_to_message_id=message.message_id,
    )
    await send_menu_keyboard(message.answer, message, state, session)
