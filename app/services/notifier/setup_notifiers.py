from aiogram import Bot


from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.notifier.antifreeze import AntifreezeNotifier
from app.services.notifier.base import Notifier
from app.services.notifier.bonus import BonusCheckNotifier, BonusNotifier
from app.services.notifier.cleaning import CleaningNotifier
from app.services.notifier.manual_start.alerter import ManualStartAlerter

from app.services.notifier.manual_start.notifier import ManualStartNotifier
from app.services.notifier.manual_start.reminder import ManualStartReminder
from app.services.notifier.monthly_report.monthly_report import MonthlyReportNotifier
from app.services.notifier.payment_check.alert import PaymentCheckAlertNotifier
from app.services.notifier.payment_check.payment_check import PaymentCheckNotifier
from app.services.notifier.promocode import PromocodeCheckNotifier, PromocodeNotifier
from app.services.notifier.refund import RefundNotifier
from app.services.notifier.shifts.close import CloseShiftNotifier
from app.services.notifier.shifts.open import OpenShiftNotifier
from app.services.notifier.shifts.shift_close_open import CloseOpenShiftNotifier


def setup_common_notifiers(bot: Bot, session: async_sessionmaker) -> list[Notifier]:
    notifiers = [
        ManualStartNotifier(bot, session),
        ManualStartAlerter(bot, session),
        ManualStartReminder(bot, session),
        AntifreezeNotifier(bot, session),
        RefundNotifier(bot, session),
        CleaningNotifier(bot, session),
    ]
    return notifiers


def setup_promocode_and_bonus_notifiers(
    bot: Bot, session: async_sessionmaker
) -> list[Notifier]:
    notifiers = [BonusNotifier(bot, session), PromocodeNotifier(bot, session)]
    return notifiers


def setup_shifts_notifiers(bot: Bot, session: async_sessionmaker) -> list[Notifier]:
    return [CloseOpenShiftNotifier(bot, session)]


def setup_monthly_report_notifiers(
    bot: Bot, session: async_sessionmaker
) -> list[Notifier]:
    return [MonthlyReportNotifier(bot, session)]


def setup_payment_check_notifiers(
    bot: Bot, session: async_sessionmaker
) -> list[Notifier]:
    return [PaymentCheckNotifier(bot, session), PaymentCheckAlertNotifier(bot, session)]


def setup_bonus_promo_check_notifiers(
    bot: Bot, session: async_sessionmaker
) -> list[Notifier]:
    return [BonusCheckNotifier(bot, session), PromocodeCheckNotifier(bot, session)]
