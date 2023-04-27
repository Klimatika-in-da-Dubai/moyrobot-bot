from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.antifreeze import Antifreeze


class AntifreezeDAO(BaseDAO[Antifreeze]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Antifreeze, session)

    async def add_bonus(self, antifreeze: Antifreeze):
        async with self._session() as session:
            await session.merge(antifreeze)
            await session.commit()
