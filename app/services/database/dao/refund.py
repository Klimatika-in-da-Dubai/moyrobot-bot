from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.refund import Refund


class RefundDAO(BaseDAO[Refund]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Refund, session)

    async def add_refund(self, refund: Refund):
        async with self._session() as session:
            await session.merge(refund)
            await session.commit()
