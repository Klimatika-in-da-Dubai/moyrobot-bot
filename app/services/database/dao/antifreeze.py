from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.antifreeze import Antifreeze


class AntifreezeDAO(BaseDAO[Antifreeze]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Antifreeze, session)

    async def add_bonus(self, antifreeze: Antifreeze):
        async with self._session() as session:
            await session.merge(antifreeze)
            await session.commit()

    async def get_unnotified(self) -> Sequence[Antifreeze]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(Antifreeze).where(Antifreeze.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def make_notified(self, antifreeze: Antifreeze):
        async with self._session() as session:
            await session.execute(
                update(Antifreeze)
                .where(Antifreeze.id == antifreeze.id)
                .values(notified=True)
            )
            await session.commit()
