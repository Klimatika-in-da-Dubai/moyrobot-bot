from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.notifier.base import Notifier

from app.services.parser.parser import Parser
from app.services.scheduler.notifiers import notify
from app.services.scheduler.update_db import update_db


def get_scheduler(
    bot: Bot,
    parser: Parser,
    session: async_sessionmaker[AsyncSession],
    common_notifiers: list[Notifier],
    bonus_promo_notifiers: list[Notifier],
    shift_notifier: list[Notifier],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_db, "interval", seconds=30, args=(parser, session))
    scheduler.add_job(notify, "interval", seconds=10, args=(common_notifiers,))
    scheduler.add_job(notify, "cron", hour="9", args=(bonus_promo_notifiers,))
    scheduler.add_job(notify, "interval", seconds=10, args=(shift_notifier,))

    return scheduler
