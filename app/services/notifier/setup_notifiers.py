from aiogram import Bot


from sqlalchemy.ext.asyncio import AsyncSession
from app.services.notifier.antifreeze import AntifreezeNotifier
from app.services.notifier.base import Notifier
from app.services.notifier.bonus import BonusCheckNotifier, BonusNotifier
from app.services.notifier.cleaning import CleaningNotifier
from app.services.notifier.consumable_request import ConsumableRequestNotifier
from app.services.notifier.corporate_report import CorporateReportNotifier
from app.services.notifier.manual_start.alerter import ManualStartAlerter

from app.services.notifier.manual_start.notifier import ManualStartNotifier
from app.services.notifier.manual_start.reminder import ManualStartReminder
from app.services.notifier.monthly_report.monthly_report import MonthlyReportNotifier
from app.services.notifier.operator_request import OperatorRequestNotifier
from app.services.notifier.payment_check.alert import PaymentCheckAlertNotifier
from app.services.notifier.payment_check.payment_check import PaymentCheckNotifier
from app.services.notifier.promocode import PromocodeCheckNotifier, PromocodeNotifier
from app.services.notifier.refund import RefundNotifier
from app.services.notifier.shifts.shift_close_open import CloseOpenShiftNotifier


def setup_common_notifiers() -> list[Notifier]:
    notifiers = [
        ManualStartNotifier,
        ManualStartAlerter,
        ManualStartReminder,
        AntifreezeNotifier,
        RefundNotifier,
        CleaningNotifier,
    ]
    return notifiers


def setup_promocode_and_bonus_notifiers() -> list[Notifier]:
    notifiers = [BonusNotifier, PromocodeNotifier]
    return notifiers


def setup_shifts_notifiers() -> list[Notifier]:
    notifiers = [CloseOpenShiftNotifier]
    return notifiers


def setup_monthly_report_notifiers() -> list[Notifier]:
    notifiers = [MonthlyReportNotifier]
    return notifiers


def setup_payment_check_notifiers() -> list[Notifier]:
    notifiers = [PaymentCheckNotifier, PaymentCheckAlertNotifier]
    return notifiers


def setup_bonus_promo_check_notifiers() -> list[Notifier]:
    notifiers = [BonusCheckNotifier, PromocodeCheckNotifier]
    return notifiers


def setup_requests_notifiers() -> list[Notifier]:
    notifiers = [
        OperatorRequestNotifier,
        ConsumableRequestNotifier,
    ]
    return notifiers


def setup_corporate_report_notifiers() -> list[Notifier]:
    notifiers = [CorporateReportNotifier]
    return notifiers
