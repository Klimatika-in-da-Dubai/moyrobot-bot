from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.refund import Refund


class RefundDAO(BaseDAO[Refund]):
    def __init__(self, session: AsyncSession):
        super().__init__(Refund, session)

    async def add_refund(self, refund: Refund):
        await self._session.merge(refund)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Refund]:
        bonuses = await self._session.execute(
            select(Refund).where(Refund.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def make_notified(self, refund: Refund):
        await self._session.execute(
            update(Refund).where(Refund.id == refund.id).values(notified=True)
        )
        await self._session.commit()
