from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.cleaning import Cleaning


class CleaningDAO(BaseDAO[Cleaning]):
    def __init__(self, session: async_sessionmaker):
        super().__init__(Cleaning, session)

    async def add_cleaning(self, cleaning: Cleaning):
        async with self._session() as session:
            await session.merge(cleaning)
            await session.commit()

    async def get_unnotified(self) -> Sequence[Cleaning]:
        async with self._session() as session:
            cleanings = await session.execute(
                select(Cleaning).where(Cleaning.notified.is_(False))
            )
            return cleanings.scalars().all()

    async def make_notified(self, cleaning: Cleaning):
        async with self._session() as session:
            await session.execute(
                update(Cleaning).where(Cleaning.id == cleaning.id).values(notified=True)
            )
            await session.commit()

    async def set_approved_by_id(self, cleaning_id: int, value: bool):
        async with self._session() as session:
            await session.execute(
                update(Cleaning)
                .where(Cleaning.id == cleaning_id)
                .values(approved=value)
            )
            await session.commit()
