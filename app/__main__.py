import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.core.handlers import handlers_router
from app.core.middlewares.db import DbSessionMiddleware
from app.services.database.connector import setup_get_pool
from app.services.parser.parser import Parser
from app.services.parser.terminal_session import TerminalSession
from app.services.scheduler.scheduler import get_scheduler
from app.settings.config import Config, load_config


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(handlers_router)


def setup_middlewares(dp: Dispatcher, session) -> None:
    dp.update.middleware(DbSessionMiddleware(session))


def get_terminal_sessions(config: Config) -> list[TerminalSession]:
    sessions = [
        TerminalSession(terminal.id, terminal.url, terminal.login, terminal.password)
        for terminal in config.terminals
    ]
    return sessions


def get_parser(terminal_sessions: list[TerminalSession]) -> Parser:
    return Parser(terminal_sessions)


async def main():
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)s] - %(name)s -"
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        level=logging.DEBUG,
    )
    config: Config = load_config()
    bot = Bot(config.bot.token, parse_mode=config.bot.parse_mode)
    session = await setup_get_pool(config.db.uri)
    terminal_sessions = get_terminal_sessions(config)
    parser = get_parser(terminal_sessions)
    dp = Dispatcher(storage=RedisStorage.from_url(config.redis.url))
    scheduler = get_scheduler(bot, parser, session)
    setup_routers(dp)
    setup_middlewares(dp, session)
    try:
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()


if __name__ == "__main__":
    asyncio.run(main())
