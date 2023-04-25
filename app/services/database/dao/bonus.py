from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.bonus import Bonus


class BonusDAO(BaseDAO[Bonus]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Bonus, session)

    async def add_bonus(self, promocode: Bonus):
        async with self._session() as session:
            await session.merge(promocode)
            await session.commit()
