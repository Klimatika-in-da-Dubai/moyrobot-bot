from datetime import datetime
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.bonus import Bonus


class BonusDAO(BaseDAO[Bonus]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Bonus, session)

    async def add_bonus(self, bonus: Bonus):
        async with self._session() as session:
            await session.merge(bonus)
            await session.commit()

    async def get_unnotified(self) -> Sequence[Bonus]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(Bonus).where(Bonus.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[Bonus]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(Bonus)
                .filter(Bonus.date.between(begin, end))
                .where(Bonus.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def make_notified(self, bonus: Bonus):
        async with self._session() as session:
            await session.execute(
                update(Bonus).where(Bonus.id == bonus.id).values(notified=True)
            )
            await session.commit()
