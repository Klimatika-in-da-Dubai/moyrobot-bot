from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.mailing import GroupMailing, Mailing, MailingType


class MailingDAO(BaseDAO[Mailing]):
    """ORM queries for users table"""

    def __init__(self, session: async_sessionmaker):
        super().__init__(Mailing, session)

    async def add_mailing(self, mailing: Mailing) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(mailing)
            await session.commit()

    async def get_mailing_ids(self, type: MailingType):
        async with self._session() as session:
            ids = await session.execute(select(Mailing.id).where(Mailing.type == type))
            return ids.scalars().all()


class GroupMailingDAO(BaseDAO[GroupMailing]):
    """ORM queries for users table"""

    def __init__(self, session: async_sessionmaker):
        super().__init__(GroupMailing, session)

    async def add_mailing(self, mailing: GroupMailing) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(mailing)
            await session.commit()

    async def get_mailing_ids(self, type: MailingType):
        async with self._session() as session:
            ids = await session.execute(
                select(GroupMailing.id).where(GroupMailing.type == type)
            )
            return ids.scalars().all()


async def get_mailing_ids(session: async_sessionmaker, type: MailingType):
    ids = []
    ids.extend(await MailingDAO(session).get_mailing_ids(type))
    ids.extend(await GroupMailingDAO(session).get_mailing_ids(type))
    return ids
