from datetime import timedelta
from typing import List
from aiogram.enums import InputMediaType
from aiogram.types import InputMediaPhoto
from app.core.keyboards.notifications.operator_request import (
    get_operator_request_keyboard,
)
from app.services.database.dao.operator_request import OperatorRequestDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.operator_request import OperatorRequest
from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class OperatorRequestNotifier(Notifier):
    def __init__(self, bot, session, *args):
        super().__init__(
            bot, session, MailingType.OPERATOR_REQUEST, OperatorRequestDAO(session)
        )
        self._dao: OperatorRequestDAO
        self._userdao = UserDAO(session)

    async def get_objects_to_notify(self):
        delta_between_notifies = timedelta(hours=1)
        return await self._dao.get_requests_to_notify(delta_between_notifies)

    async def make_notified(self, operator_request: OperatorRequest) -> None:
        await self._dao.make_notified(operator_request)

    async def send_notify(
        self, id: int, operator_request: OperatorRequest, debug: bool = False
    ):
        text = await self.get_text(operator_request)

        match len(operator_request.photos):
            case 0:
                message = await self._bot.send_message(
                    id,
                    text=text,
                    reply_markup=get_operator_request_keyboard(operator_request),
                )
            case 1:
                message = await self._bot.send_photo(
                    id,
                    photo=operator_request.photos[0],
                    caption=text,
                    reply_markup=get_operator_request_keyboard(operator_request),
                )
            case _:
                media_group = self.get_media_group(operator_request, text)
                await self._bot.send_media_group(id, media_group)  # type: ignore
                message = await self._bot.send_message(
                    id,
                    text=text,
                    reply_markup=get_operator_request_keyboard(operator_request),
                )

        await self._dao.add_notify_message_id(operator_request, id, message.message_id)
        await self._dao.make_notified(operator_request)

    async def get_text(self, operator_request: OperatorRequest) -> str:
        user_name = await self._userdao.get_user_name_by_id(
            operator_request.from_user_id
        )
        date = operator_request.date.strftime("%d.%m.%Y %H:%M")
        return (
            f"*Получено от пользователя:* {escape_chars(user_name)}\n"
            f"*Дата:* {escape_chars(date)}\n\n"
            f"{operator_request.md_text}"
        )

    def get_media_group(
        self, operator_request: OperatorRequest, text: str
    ) -> List[InputMediaPhoto]:
        media_group = [
            InputMediaPhoto(type=InputMediaType.PHOTO, media=photo)
            for photo in operator_request.photos
        ]
        return media_group
