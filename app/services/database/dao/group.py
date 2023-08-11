from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.group import Group


class GroupDAO(BaseDAO[Group]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Group, session)

    async def add_group(self, group: Group):
        async with self._session() as session:
            await session.merge(group)
            await session.commit()

    async def delete_group_by_id(self, id: int):
        async with self._session() as session:
            await session.execute(delete(Group).where(Group.id == id))
            await session.commit()
