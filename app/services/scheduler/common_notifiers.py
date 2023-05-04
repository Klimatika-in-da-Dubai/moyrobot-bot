from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.notifier.manual_start.notifier import ManualStartNotifier
from app.services.notifier.refund import RefundNotifier
from app.services.notifier.shifts.close import CloseShiftNotifier
from app.services.notifier.shifts.open import OpenShiftNotifier


async def notify(bot: Bot, session: async_sessionmaker):
    manual_start_notifier = ManualStartNotifier(bot, session)
    refund_notifier = RefundNotifier(bot, session)
    await manual_start_notifier.notify()
    await refund_notifier.notify()
