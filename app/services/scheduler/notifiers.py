from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.notifier.base import Notifier


async def notify(
    notifiers: list[type[Notifier]],
    bot: Bot,
    sessionmaker: async_sessionmaker,
    client_db_sessionmaker: async_sessionmaker,
):
    async with sessionmaker() as session:
        async with client_db_sessionmaker() as client_db_session:
            for notifier in notifiers:
                await notifier(bot, session, client_db_session).notify()  # type: ignore
