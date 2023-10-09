from app.services.notifier.base import Notifier


async def notify(notifiers: list[type[Notifier]], bot, sessionmaker):
    async with sessionmaker() as session:
        for notifier in notifiers:
            await notifier(bot, session).notify()  # type: ignore
