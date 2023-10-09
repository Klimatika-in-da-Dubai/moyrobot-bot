from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.corporation import Corporation


class CorporationDAO(BaseDAO[Corporation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Corporation, session)

    async def get_name(self, corporation_id: int) -> str:
        result = await self._session.execute(
            select(Corporation.name).where(Corporation.id == corporation_id)
        )
        return result.scalar_one()
