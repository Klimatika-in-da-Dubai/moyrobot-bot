from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.antifreeze import Antifreeze


class AntifreezeDAO(BaseDAO[Antifreeze]):
    def __init__(self, session: AsyncSession):
        super().__init__(Antifreeze, session)

    async def add_bonus(self, antifreeze: Antifreeze):
        await self._session.merge(antifreeze)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Antifreeze]:
        bonuses = await self._session.execute(
            select(Antifreeze).where(Antifreeze.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def make_notified(self, antifreeze: Antifreeze):
        await self._session.execute(
            update(Antifreeze)
            .where(Antifreeze.id == antifreeze.id)
            .values(notified=True)
        )
        await self._session.commit()
