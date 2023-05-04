from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.manual_start import ManualStart

from app.services.parser.parser import Parser


async def update_db(parser: Parser, session: async_sessionmaker[AsyncSession]):
    manual_starts = await parser.get_manual_starts()
    manual_start_dao = ManualStartDAO(session)
    for manual_start in manual_starts:
        db_manual_start: ManualStart = await manual_start_dao.get_by_id(
            id_=manual_start.id
        )
        if db_manual_start is None:
            await manual_start_dao.add_manual_start(manual_start)
            continue

        if db_manual_start.mode is None:
            await manual_start_dao.update_manual_start_mode(manual_start)
