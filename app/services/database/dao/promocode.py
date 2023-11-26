import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.promocode import Promocode


class PromocodeDAO(BaseDAO[Promocode]):
    def __init__(self, session: AsyncSession):
        super().__init__(Promocode, session)

    async def add_promocode(self, promocode: Promocode):
        await self._session.merge(promocode)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Promocode]:
        bonuses = await self._session.execute(
            select(Promocode).where(Promocode.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> Sequence[Promocode]:
        bonuses = await self._session.execute(
            select(Promocode)
            .filter(Promocode.date.between(begin, end))
            .where(Promocode.notified == False)  # noqa: E712
            .order_by(Promocode.date)
        )
        return bonuses.scalars().all()

    async def get_between_time(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> Sequence[Promocode]:
        bonuses = await self._session.execute(
            select(Promocode)
            .filter(Promocode.date.between(begin, end))
            .order_by(Promocode.date)
        )
        return bonuses.scalars().all()

    async def make_notified(self, promocode: Promocode):
        await self._session.execute(
            update(Promocode).where(Promocode.id == promocode.id).values(notified=True)
        )
        await self._session.commit()
