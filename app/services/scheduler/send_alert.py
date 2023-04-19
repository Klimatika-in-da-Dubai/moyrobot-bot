import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.database.dao.mailing import get_mailing_ids
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType


async def send_manual_starts_alert(bot: Bot, session: async_sessionmaker):
    manual_start_dao = ManualStartDAO(session)
    manual_starts_to_alert = await manual_start_dao.get_unalerted_manual_starts(
        datetime.timedelta(minutes=3)
    )
    ids = await get_mailing_ids(session, MailingType.MANUAL_START_ALERT)
    for manual_start in manual_starts_to_alert:
        await manual_start_dao.set_sended_to_chat(manual_start, True)

        date = manual_start.date.strftime('%Y\-%m\-%d %H:%M:%S')

        text = (
            "Не было получена отчёта по ручному запуску\n\n"
            f"*ID:* {manual_start.id}\n"
            f"*Дата\-время:* {date} \n"
        )

        for id in ids:
            await bot.send_message(id, text=text)
