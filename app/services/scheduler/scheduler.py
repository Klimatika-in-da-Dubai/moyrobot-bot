from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.notifier.base import Notifier

from app.services.parser.parser import Parser
from app.services.scheduler.bonus_check import create_bonus_check_for_past_week
from app.services.scheduler.notifiers import notify
from app.services.scheduler.payment_check import create_payment_check_for_past_day
from app.services.scheduler.promo_check import create_promocode_check_for_past_week
from app.services.scheduler.update_db import update_db


def get_scheduler(
    bot: Bot,
    parser: Parser,
    session: async_sessionmaker[AsyncSession],
    common_notifiers: list[Notifier],
    bonus_promo_notifiers: list[Notifier],
    shift_notifiers: list[Notifier],
    monthly_report_notifiers: list[Notifier],
    payment_check_notifiers: list[Notifier],
    bonus_promo_check_notifiers: list[Notifier],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        create_payment_check_for_past_day,
        "cron",
        hour="6",
        args=(session,),
    )

    scheduler.add_job(
        create_bonus_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(session,),
    )
    scheduler.add_job(
        create_promocode_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(session,),
    )

    scheduler.add_job(update_db, "interval", seconds=30, args=(parser, session))
    scheduler.add_job(notify, "interval", seconds=10, args=(common_notifiers,))

    scheduler.add_job(notify, "cron", hour="9", args=(bonus_promo_notifiers,))
    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(payment_check_notifiers,),
    )

    scheduler.add_job(notify, "interval", seconds=10, args=(shift_notifiers,))
    scheduler.add_job(notify, "cron", day="1,16", args=(monthly_report_notifiers,))

    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(bonus_promo_check_notifiers,),
    )
    return scheduler
