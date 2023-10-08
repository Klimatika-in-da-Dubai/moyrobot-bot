from datetime import datetime
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.bonus import Bonus


class BonusDAO(BaseDAO[Bonus]):
    def __init__(self, session: AsyncSession):
        super().__init__(Bonus, session)

    async def add_bonus(self, bonus: Bonus):
        await self._session.merge(bonus)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus).where(Bonus.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus)
            .filter(Bonus.date.between(begin, end))
            .where(Bonus.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def get_between_time(self, begin: datetime, end: datetime) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus).filter(Bonus.date.between(begin, end))
        )
        return bonuses.scalars().all()

    async def make_notified(self, bonus: Bonus):
        await self._session.execute(
            update(Bonus).where(Bonus.id == bonus.id).values(notified=True)
        )
        await self._session.commit()
