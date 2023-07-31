import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.handlers import handlers_router
from app.core.middlewares.db import DbSessionMiddleware
from app.services.database.connector import setup_get_pool
from app.services.notifier.setup_notifiers import (
    setup_bonus_promo_check_notifiers,
    setup_common_notifiers,
    setup_corporate_report_notifiers,
    setup_monthly_report_notifiers,
    setup_payment_check_notifiers,
    setup_promocode_and_bonus_notifiers,
    setup_shifts_notifiers,
)
from app.services.parser.parser import Parser
from app.services.parser.terminal_session import TerminalSession
from app.services.scheduler.scheduler import get_scheduler
from app.settings.config import Config, load_config


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(handlers_router)


def setup_middlewares(dp: Dispatcher, session) -> None:
    dp.update.middleware(DbSessionMiddleware(session))


def get_parser(config: Config) -> Parser:
    sessions = [
        TerminalSession(terminal.id, terminal.url, terminal.login, terminal.password)
        for terminal in config.terminals
    ]
    return Parser(sessions)


def setup_scheduler(bot: Bot, session: async_sessionmaker, parser: Parser):
    common_notifiers = setup_common_notifiers(bot, session)
    bonus_promo_notifiers = setup_promocode_and_bonus_notifiers(bot, session)
    shift_notifier = setup_shifts_notifiers(bot, session)
    monthly_report_notifiers = setup_monthly_report_notifiers(bot, session)
    payment_check_notifiers = setup_payment_check_notifiers(bot, session)
    bonus_promo_check_notifiers = setup_bonus_promo_check_notifiers(bot, session)
    corporate_report_notitifiers = setup_corporate_report_notifiers(bot, session)

    return get_scheduler(
        parser,
        session,
        common_notifiers,
        bonus_promo_notifiers,
        shift_notifier,
        monthly_report_notifiers,
        payment_check_notifiers,
        bonus_promo_check_notifiers,
        corporate_report_notitifiers,
    )


async def main():
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)s] - %(name)s -"
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        level=logging.DEBUG,
    )

    config: Config = load_config()
    bot = Bot(config.bot.token, parse_mode=config.bot.parse_mode)
    session = await setup_get_pool(config.db.uri)
    parser = get_parser(config)
    dp = Dispatcher(storage=RedisStorage.from_url(config.redis.url))
    scheduler = setup_scheduler(bot, session, parser)
    setup_routers(dp)
    setup_middlewares(dp, session)
    try:
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()


if __name__ == "__main__":
    asyncio.run(main())
