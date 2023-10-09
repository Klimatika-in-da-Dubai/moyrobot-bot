from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.group import Group


class GroupDAO(BaseDAO[Group]):
    def __init__(self, session: AsyncSession):
        super().__init__(Group, session)

    async def add_group(self, group: Group):
        await self._session.merge(group)
        await self._session.commit()

    async def delete_group_by_id(self, id: int):
        await self._session.execute(delete(Group).where(Group.id == id))
        await self._session.commit()
