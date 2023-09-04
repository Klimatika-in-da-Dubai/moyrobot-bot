from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.notifier.base import Notifier
from app.services.notifier.setup_notifiers import (
    setup_bonus_promo_check_notifiers,
    setup_common_notifiers,
    setup_corporate_report_notifiers,
    setup_monthly_report_notifiers,
    setup_payment_check_notifiers,
    setup_promocode_and_bonus_notifiers,
    setup_shifts_notifiers,
)
from app.services.notifier.shifts.notify import ShiftNotifyNotifier

from app.services.parser.parser import Parser
from app.services.scheduler.auto_close_shift import auto_close_shift
from app.services.scheduler.bonus_check import create_bonus_check_for_past_week
from app.services.scheduler.corporate_report import (
    create_corporate_report_for_past_month,
)
from app.services.scheduler.notifiers import notify
from app.services.scheduler.payment_check import create_payment_check_for_past_day
from app.services.scheduler.promo_check import create_promocode_check_for_past_week
from app.services.scheduler.update_db import update_db


def get_scheduler(
    bot: Bot,
    parser: Parser,
    session: async_sessionmaker[AsyncSession],
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
        name="Creation corporate_report",
    )
    scheduler.add_job(
        update_db,
        "interval",
        seconds=30,
        args=(parser, session),
        name="MoyRobotDB update",
    )
    add_common_notifiers_job(scheduler, bot, session)
    add_bonus_promo_job(scheduler, bot, session)
    add_payment_check_job(scheduler, bot, session)
    add_shift_notifiers_job(scheduler, bot, session)
    add_monthly_report_job(scheduler, bot, session)
    add_corporate_report_job(scheduler, bot, session)
    add_bonus_promo_check_job(scheduler, bot, session)
    add_shift_alert_job(scheduler, bot, session)
    add_auto_close_shift_job(scheduler, bot, session)
    return scheduler


def add_common_notifiers_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    common_notifiers = setup_common_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "interval",
        seconds=10,
        args=(common_notifiers,),
        name="Common notifiers",
    )


def add_bonus_promo_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    bonus_promo_notifiers = setup_promocode_and_bonus_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "cron",
        hour="9",
        args=(bonus_promo_notifiers,),
        name="Bonus and Promocode notifiers",
    )


def add_payment_check_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    payment_check_notifiers = setup_payment_check_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(payment_check_notifiers,),
        name="Payment Chtck notifiers",
    )


def add_shift_notifiers_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    shift_notifiers = setup_shifts_notifiers(bot, session)
    scheduler.add_job(
        notify, "interval", seconds=10, args=(shift_notifiers,), name="Shift notifiers"
    )


def add_monthly_report_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    monthly_report_notifiers = setup_monthly_report_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "cron",
        day="1,16",
        hour="12",
        args=(monthly_report_notifiers,),
        name="Monthly Report notifiers",
    )


def add_corporate_report_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    corporate_report_notifiers = setup_corporate_report_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "cron",
        day="1",
        hour="9",
        args=(corporate_report_notifiers,),
        name="Corporate Report notifiers",
    )


def add_bonus_promo_check_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    bonus_promo_check_notifiers = setup_bonus_promo_check_notifiers(bot, session)
    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(bonus_promo_check_notifiers,),
        name="Bonus and Promocode check notifiers",
    )


def add_shift_alert_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    scheduler.add_job(
        notify,
        "cron",
        minute="*/15",
        args=([ShiftNotifyNotifier(bot, session)],),
        name="ShiftNotifyNotifier",
    )


def add_auto_close_shift_job(
    scheduler: AsyncIOScheduler, bot: Bot, session: async_sessionmaker
):
    scheduler.add_job(
        auto_close_shift,
        "cron",
        hour="9-12,21-23",
        minute="*/30",
        args=(bot, session),
        name="Auto Close Shift",
    )
