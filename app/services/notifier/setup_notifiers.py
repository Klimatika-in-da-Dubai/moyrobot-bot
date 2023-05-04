from aiogram import Bot


from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.notifier.antifreeze import AntifreezeNotifier
from app.services.notifier.base import Notifier
from app.services.notifier.bonus import BonusNotifier
from app.services.notifier.manual_start.alerter import ManualStartAlerter

from app.services.notifier.manual_start.notifier import ManualStartNotifier
from app.services.notifier.manual_start.reminder import ManualStartReminder
from app.services.notifier.promocode import PromocodeNotifier
from app.services.notifier.refund import RefundNotifier


def setup_common_notifiers(bot: Bot, session: async_sessionmaker) -> list[Notifier]:
    notifiers = []
    notifiers.append(ManualStartNotifier(bot, session))
    notifiers.append(ManualStartAlerter(bot, session))
    notifiers.append(ManualStartReminder(bot, session))
    notifiers.append(BonusNotifier(bot, session))
    notifiers.append(AntifreezeNotifier(bot, session))
    notifiers.append(PromocodeNotifier(bot, session))
    notifiers.append(RefundNotifier(bot, session))
    return notifiers
