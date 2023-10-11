from collections.abc import Sequence
from datetime import datetime
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.cashbox_replenishment import CashboxReplenishment


class CashboxReplenishmentDAO(BaseDAO):
    def __init__(self, session: AsyncSession):
        super().__init__(CashboxReplenishment, session)

    async def add_cashbox_replenishment(
        self, cashbox_replenishment: CashboxReplenishment
    ):
        await self._session.merge(cashbox_replenishment)
        await self._session.commit()

    async def get_cashbox_replenishment_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[CashboxReplenishment]:
        collections = await self._session.execute(
            select(CashboxReplenishment).filter(
                CashboxReplenishment.date.between(begin, end)
            )
        )
        return collections.scalars().all()

    async def get_unnotified(self) -> Sequence[CashboxReplenishment]:
        collections = await self._session.execute(
            select(CashboxReplenishment).where(CashboxReplenishment.notified.is_(False))
        )
        return collections.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[CashboxReplenishment]:
        collections = await self._session.execute(
            select(CashboxReplenishment)
            .filter(CashboxReplenishment.date.between(begin, end))
            .where(CashboxReplenishment.notified.is_(False))  # noqa: E712
        )
        return collections.scalars().all()

    async def make_notified(self, cashbox_replenishment: CashboxReplenishment):
        await self._session.execute(
            update(CashboxReplenishment)
            .where(CashboxReplenishment.id == cashbox_replenishment.id)
            .values(notified=True)
        )
        await self._session.commit()
