from typing import Sequence
from sqlalchemy import select, update
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

    async def get_unnotified(self) -> Sequence[Refund]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(Refund).where(Refund.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def make_notified(self, refund: Refund):
        async with self._session() as session:
            await session.execute(
                update(Refund).where(Refund.id == refund.id).values(notified=True)
            )
            await session.commit()
