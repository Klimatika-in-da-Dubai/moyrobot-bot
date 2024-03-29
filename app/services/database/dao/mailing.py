from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.group import Group
from app.services.database.models.mailing import GroupMailing, Mailing, MailingType
from app.services.database.models.user import User


class MailingDAO(BaseDAO[Mailing]):
    """ORM queries for users table"""

    def __init__(self, session: AsyncSession):
        super().__init__(Mailing, session)

    async def add_mailing(self, mailing: Mailing) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(mailing)
        await self._session.commit()

    async def get_mailing_ids(self, type: MailingType):
        ids = await self._session.execute(
            select(Mailing.id)
            .join(User)
            .where(User.active.is_(True))
            .where(Mailing.type == type)
        )
        return ids.scalars().all()

    async def get_user_mailings(self, user: User):
        mailings = await self._session.execute(
            select(Mailing.type).where(Mailing.id == user.id)
        )
        return mailings.scalars().all()

    async def update_user_mailings(self, user: User, new_mailings: list[Mailing]):
        await self._session.execute(delete(Mailing).where(Mailing.id == user.id))
        await self._session.commit()

        for mailing in new_mailings:
            await self.add_mailing(mailing)


class GroupMailingDAO(BaseDAO[GroupMailing]):
    """ORM queries for users table"""

    def __init__(self, session: AsyncSession):
        super().__init__(GroupMailing, session)

    async def add_mailing(self, mailing: GroupMailing) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(mailing)
        await self._session.commit()

    async def get_mailing_ids(self, type: MailingType):
        ids = await self._session.execute(
            select(GroupMailing.id).where(GroupMailing.type == type)
        )
        return ids.scalars().all()

    async def get_mailings(self, id: int) -> list[MailingType]:
        mailings = await self._session.execute(
            select(GroupMailing.type).where(GroupMailing.id == id)
        )
        return list(mailings.scalars().all())

    async def update_group_mailings(
        self, group: Group, new_mailings: list[MailingType]
    ):
        await self._session.execute(
            delete(GroupMailing).where(GroupMailing.id == group.id)
        )
        await self._session.commit()

        for mailing in new_mailings:
            await self.add_mailing(GroupMailing(id=group.id, type=mailing))


async def get_mailing_ids(session: AsyncSession, type: MailingType):
    ids = []
    ids.extend(await MailingDAO(session).get_mailing_ids(type))
    ids.extend(await GroupMailingDAO(session).get_mailing_ids(type))
    return ids
