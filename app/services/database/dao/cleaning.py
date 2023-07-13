from datetime import datetime
from typing import Sequence
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import func
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

    async def get_cleanings_between_time(
        self, start: datetime, end: datetime
    ) -> Sequence[Cleaning]:
        async with self._session() as session:
            results = await session.execute(
                select(Cleaning).where(Cleaning.date.between(start, end))
            )
            return results.scalars().all()

    async def photo_hash_already_exists(self, hash: str) -> bool:
        async with self._session() as session:
            query = text(
                "SELECT (jsonb_array_elements(jsonb_array_elements((cleaning::jsonb)->'places')->'works')->'photo_hash')::text FROM cleaning;"
            )
            result = await session.execute(query)
            return f'"{hash}"' in result.scalars().all()
