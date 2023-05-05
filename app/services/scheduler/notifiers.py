import asyncio
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.notifier.base import Notifier


async def notify(notifiers: list[Notifier]):
    tasks = [asyncio.create_task(notifier.notify()) for notifier in notifiers]
    await asyncio.gather(*tasks)
