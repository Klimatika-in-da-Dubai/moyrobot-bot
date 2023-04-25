from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.services.database.dao.base import BaseDAO
from app.services.database.models.promocode import Promocode


class PromocodeDAO(BaseDAO[Promocode]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Promocode, session)

    async def add_promocode(self, promocode: Promocode):
        async with self._session() as session:
            await session.merge(promocode)
            await session.commit()
