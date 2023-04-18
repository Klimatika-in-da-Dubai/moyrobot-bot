from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.parser.parser import Parser
from app.services.scheduler.update_db import update_db


def get_scheduler(
    parser: Parser, session: async_sessionmaker[AsyncSession]
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_db, "interval", seconds=30, args=(parser, session))
    return scheduler
