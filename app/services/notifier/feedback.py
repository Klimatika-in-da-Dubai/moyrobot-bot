from typing import List
from aiogram import Bot
from aiogram.enums import InputMediaType, ParseMode
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.notifications.feedback import get_feedback_keyboard
from app.services.database.dao.feedback import FeedbackDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.feedback import Feedback
from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class FeedbackNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, MailingType.FEEDBACK, FeedbackDAO(session))
        self._dao: FeedbackDAO
        self._userdao = UserDAO(session)

    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    async def make_notified(self, feedback: Feedback) -> None:
        await self._dao.make_notified(feedback)

    async def send_notify(self, id: int, feedback: Feedback, debug: bool = False):
        text = await self.get_text(feedback)

        if len(feedback.photos) == 0:
            await self._bot.send_message(
                id, text=text, reply_markup=get_feedback_keyboard(feedback)
            )
            return

        if len(feedback.photos) == 1:
            await self._bot.send_photo(
                id,
                photo=feedback.photos[0],
                caption=text,
                reply_markup=get_feedback_keyboard(feedback),
            )
            return

        media_group = self.get_media_group(feedback, text)
        await self._bot.send_media_group(id, media_group)  # type: ignore
        await self._bot.send_message(
            id, text=text, reply_markup=get_feedback_keyboard(feedback)
        )

    async def get_text(self, feedback: Feedback) -> str:
        user_name = await self._userdao.get_user_name_by_id(feedback.from_user_id)
        date = feedback.date.strftime("%d.%m.%Y %H:%M")
        return (
            f"*Получено от пользователя:* {escape_chars(user_name)}\n"
            f"*Дата:* {escape_chars(date)}\n\n"
            f"{feedback.md_text}"
        )

    def get_media_group(self, feedback: Feedback, text: str) -> List[InputMediaPhoto]:
        media_group = [
            InputMediaPhoto(type=InputMediaType.PHOTO, media=photo)
            for photo in feedback.photos
        ]
        return media_group
