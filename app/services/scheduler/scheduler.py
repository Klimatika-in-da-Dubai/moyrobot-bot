from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.notifier.setup_notifiers import (
    setup_bonus_promo_check_notifiers,
    setup_common_notifiers,
    setup_corporate_report_notifiers,
    setup_monthly_report_notifiers,
    setup_payment_check_notifiers,
    setup_promocode_and_bonus_notifiers,
    setup_requests_notifiers,
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
    sessionmaker: async_sessionmaker,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        create_payment_check_for_past_day,
        "cron",
        hour="6",
        args=(sessionmaker,),
        name="Creation payment_check",
    )

    scheduler.add_job(
        create_bonus_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(sessionmaker,),
        name="Creation bonus_check",
    )
    scheduler.add_job(
        create_promocode_check_for_past_week,
        "cron",
        day_of_week="0",
        hour="8",
        args=(sessionmaker,),
        name="Creation promocode_check",
    )
    scheduler.add_job(
        create_corporate_report_for_past_month,
        "cron",
        day="1",
        args=(sessionmaker,),
        name="Creation corporate_report",
    )
    scheduler.add_job(
        update_db,
        "interval",
        seconds=30,
        args=(parser, sessionmaker),
        name="MoyRobotDB update",
    )
    add_common_notifiers_job(scheduler, bot, sessionmaker)
    add_bonus_promo_job(scheduler, bot, sessionmaker)
    add_payment_check_job(scheduler, bot, sessionmaker)
    add_shift_notifiers_job(scheduler, bot, sessionmaker)
    add_monthly_report_job(scheduler, bot, sessionmaker)
    add_corporate_report_job(scheduler, bot, sessionmaker)
    add_bonus_promo_check_job(scheduler, bot, sessionmaker)
    add_shift_alert_job(scheduler, bot, sessionmaker)
    add_auto_close_shift_job(scheduler, bot, sessionmaker)
    add_request_notifiers_job(scheduler, bot, sessionmaker)
    return scheduler


def add_common_notifiers_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    common_notifiers = setup_common_notifiers()
    scheduler.add_job(
        notify,
        "interval",
        seconds=30,
        args=(common_notifiers, bot, sessionmaker),
        name="Common notifiers",
    )


def add_bonus_promo_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    bonus_promo_notifiers = setup_promocode_and_bonus_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        hour="9",
        args=(bonus_promo_notifiers, bot, sessionmaker),
        name="Bonus and Promocode notifiers",
    )


def add_payment_check_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    payment_check_notifiers = setup_payment_check_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-18",
        minute="*",
        args=(payment_check_notifiers, bot, sessionmaker),
        name="Payment Chtck notifiers",
    )


def add_request_notifiers_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    request_notifiers = setup_requests_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        hour="9-22",
        minute="*",
        args=(request_notifiers, bot, sessionmaker),
        name="Request notifiers",
    )


def add_shift_notifiers_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    shift_notifiers = setup_shifts_notifiers()
    scheduler.add_job(
        notify,
        "interval",
        seconds=10,
        args=(shift_notifiers, bot, sessionmaker),
        name="Shift notifiers",
    )


def add_monthly_report_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    monthly_report_notifiers = setup_monthly_report_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        day="1,16",
        hour="12",
        args=(monthly_report_notifiers, bot, sessionmaker),
        name="Monthly Report notifiers",
    )


def add_corporate_report_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    corporate_report_notifiers = setup_corporate_report_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        day="1",
        hour="9",
        args=(corporate_report_notifiers, bot, sessionmaker),
        name="Corporate Report notifiers",
    )


def add_bonus_promo_check_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    bonus_promo_check_notifiers = setup_bonus_promo_check_notifiers()
    scheduler.add_job(
        notify,
        "cron",
        day_of_week="0-4",
        hour="9-23",
        minute="*/30",
        args=(bonus_promo_check_notifiers, bot, sessionmaker),
        name="Bonus and Promocode check notifiers",
    )


def add_shift_alert_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    scheduler.add_job(
        notify,
        "cron",
        minute="*/15",
        args=([ShiftNotifyNotifier], bot, sessionmaker),
        name="ShiftNotifyNotifier",
    )


def add_auto_close_shift_job(
    scheduler: AsyncIOScheduler, bot: Bot, sessionmaker: async_sessionmaker
):
    scheduler.add_job(
        auto_close_shift,
        "cron",
        hour="9-12,21-23",
        minute="*/30",
        args=(bot, sessionmaker),
        name="Auto Close Shift",
    )
