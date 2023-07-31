from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.notifier.base import Notifier

from app.services.parser.parser import Parser
from app.services.scheduler.bonus_check import create_bonus_check_for_past_week
from app.services.scheduler.corporate_report import (
    create_corporate_report_for_past_month,
)
from app.services.scheduler.notifiers import notify
from app.services.scheduler.payment_check import create_payment_check_for_past_day
from app.services.scheduler.promo_check import create_promocode_check_for_past_week
from app.services.scheduler.update_db import update_db


def get_scheduler(
    parser: Parser,
    session: async_sessionmaker[AsyncSession],
    common_notifiers: list[Notifier],
    bonus_promo_notifiers: list[Notifier],
    shift_notifiers: list[Notifier],
    monthly_report_notifiers: list[Notifier],
    payment_check_notifiers: list[Notifier],
    bonus_promo_check_notifiers: list[Notifier],
    corporate_report_notifiers: list[Notifier],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        create_payment_check_for_past_day,
        "cron",
        hour="6",
        args=(session,),
        name="Creation payment_check",
    )

    scheduler.add_job(
        create_bonus_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(session,),
        name="Creation bonus_check",
    )
    scheduler.add_job(
        create_promocode_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(session,),
        name="Creation promocode_check",
    )
    scheduler.add_job(
        create_corporate_report_for_past_month,
        "cron",
        day="1",
        args=(session,),
        name="Creation corporate_reprt",
    )

    scheduler.add_job(
        create_corporate_report_for_past_month,
        "cron",
        minute="*",
        args=(session,),
        name="Creation corporate_reprt",
    )

    scheduler.add_job(
        update_db,
        "interval",
        seconds=30,
        args=(parser, session),
        name="MoyRobotDB update",
    )
    scheduler.add_job(
        notify,
        "interval",
        seconds=10,
        args=(common_notifiers,),
        name="Common notifiers",
    )

    scheduler.add_job(
        notify,
        "cron",
        hour="9",
        args=(bonus_promo_notifiers,),
        name="Bonus and Promocode notifiers",
    )

    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(payment_check_notifiers,),
        name="Payment Chtck notifiers",
    )

    scheduler.add_job(
        notify, "interval", seconds=10, args=(shift_notifiers,), name="Shift notifiers"
    )

    scheduler.add_job(
        notify,
        "cron",
        day="1,16",
        args=(monthly_report_notifiers,),
        name="Monthly Report notifiers",
    )

    scheduler.add_job(
        notify,
        "cron",
        day="1",
        hour="9",
        args=(corporate_report_notifiers,),
        name="Corporate Report notifiers",
    )

    # Удалить
    scheduler.add_job(
        notify,
        "interval",
        seconds=10,
        args=(corporate_report_notifiers,),
        name="Corporate Report notifiers",
    )
    ####

    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(bonus_promo_check_notifiers,),
        name="Bonus and Promocode check notifiers",
    )
    return scheduler
