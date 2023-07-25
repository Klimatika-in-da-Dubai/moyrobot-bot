from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.corporation import Corporation


class CorporationDAO(BaseDAO[Corporation]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Corporation, session)

    async def get_name(self, corporation_id: int) -> str:
        async with self._session() as session:
            result = await session.execute(
                select(Corporation.name).where(Corporation.id == corporation_id)
            )
            return result.scalar_one()
