from app.services.notifier.base import Notifier


async def notify(notifiers: list[Notifier]):
    for notifier in notifiers:
        await notifier.notify()
