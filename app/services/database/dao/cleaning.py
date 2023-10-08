from datetime import datetime
from typing import Sequence
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.cleaning import Cleaning


class CleaningDAO(BaseDAO[Cleaning]):
    def __init__(self, session: AsyncSession):
        super().__init__(Cleaning, session)

    async def add_cleaning(self, cleaning: Cleaning):
        await self._session.merge(cleaning)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Cleaning]:
        cleanings = await self._session.execute(
            select(Cleaning).where(Cleaning.notified.is_(False))
        )
        return cleanings.scalars().all()

    async def make_notified(self, cleaning: Cleaning):
        await self._session.execute(
            update(Cleaning).where(Cleaning.id == cleaning.id).values(notified=True)
        )
        await self._session.commit()

    async def set_approved_by_id(self, cleaning_id: int, value: bool):
        await self._session.execute(
            update(Cleaning).where(Cleaning.id == cleaning_id).values(approved=value)
        )
        await self._session.commit()

    async def get_cleanings_between_time(
        self, start: datetime, end: datetime
    ) -> Sequence[Cleaning]:
        results = await self._session.execute(
            select(Cleaning).where(Cleaning.date.between(start, end))
        )
        return results.scalars().all()

    async def photo_hash_already_exists(self, hash: str) -> bool:
        query = text(
            "SELECT (jsonb_array_elements(jsonb_array_elements((cleaning::jsonb)->'places')"
            "->'works')->'photo_hash')::text FROM cleaning;"
        )
        result = await self._session.execute(query)
        return f'"{hash}"' in result.scalars().all()
