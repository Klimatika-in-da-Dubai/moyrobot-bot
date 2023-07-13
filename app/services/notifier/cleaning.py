from aiogram import Bot, types
from aiogram.enums import InputMediaType
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from app.core.keyboards.operator.cleaning.approve import get_cleaning_approve_keyboard
from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.dto.cleaning import CleaningDTO
from app.services.database.models.cleaning import Cleaning
from app.services.database.models.mailing import MailingType
from app.services.notifier.base import Notifier
from app.utils.text import escape_chars


class CleaningNotifier(Notifier):
    def __init__(self, bot: Bot, session: async_sessionmaker):
        super().__init__(bot, session, MailingType.CLEANING, CleaningDAO(session))
        self._dao: CleaningDAO

    async def get_objects_to_notify(self):
        return await self._dao.get_unnotified()

    async def make_notified(self, cleaning: Cleaning) -> None:
        await self._dao.make_notified(cleaning)

    def get_media_group(self, cleaning: Cleaning, debug: bool):
        cleaningdto = CleaningDTO.from_db(cleaning.cleaning)
        media_group = []
        for place in cleaningdto.places:
            for work in place.works:
                caption = f"{place.name}: {work.name}"
                if debug:
                    caption += f"\n{escape_chars(work.photo_file_id)}"

                media = types.InputMediaPhoto(
                    type=InputMediaType.PHOTO,
                    media=work.photo_file_id,
                    caption=caption,
                )
                media_group.append(media)
        return media_group

    async def send_notify(self, id: int, cleaning: Cleaning, debug: bool = False):
        media_group = self.get_media_group(cleaning, debug)
        count_messages = len(media_group) // 10
        for i in range(count_messages):
            start = i * 10
            end = i * 10 + 10
            await self._bot.send_media_group(chat_id=id, media=media_group[start:end])
        start = (count_messages) * 10
        await self._bot.send_media_group(chat_id=id, media=media_group[start:])
        await self._bot.send_message(
            chat_id=id,
            text="Получен отчёт об уборке",
            reply_markup=get_cleaning_approve_keyboard(cleaning.id),
        )
