from typing import Sequence
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from app.services.database.dao.base import BaseDAO
from app.services.database.models.user import Role, User, UserRole


class UserDAO(BaseDAO[User]):
    """ORM queries for users table"""

    def __init__(self, session: async_sessionmaker):
        super().__init__(User, session)

    async def add_user(self, user: User) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(user)
            await session.commit()

    async def add_user_with_roles(self, user: User, user_roles: list[UserRole]):
        await self.add_user(user)

        async with self._session() as session:
            for user_role in user_roles:
                await session.merge(user_role)

            await session.commit()

    async def get_user_roles(self, user: User) -> Sequence[Role]:
        async with self._session() as session:
            roles = await session.execute(
                select(UserRole.role).join(User).where(self._model.id == user.id)
            )
            roles_list = roles.scalars().all()
            return roles_list

    async def get_ids_to_report_test_manual_start(self) -> Sequence[int]:
        async with self._session() as session:
            ids = await session.execute(
                select(UserRole.id).where(UserRole.role == Role.ADMIN)
            )
            return ids.scalars().all()

    async def get_ids_to_report_service_manual_start(self) -> Sequence[int]:
        async with self._session() as session:
            ids = await session.execute(
                select(UserRole.id).where(UserRole.role == Role.ADMIN)
            )
            return ids.scalars().all()

    async def get_ids_to_report_rewash_manual_start(self) -> Sequence[int]:
        async with self._session() as session:
            ids = await session.execute(
                select(UserRole.id).where(UserRole.role == Role.ADMIN)
            )
            return ids.scalars().all()

    async def get_ids_to_report_paid_manual_start(self) -> Sequence[int]:
        async with self._session() as session:
            ids = await session.execute(
                select(UserRole.id).where(UserRole.role == Role.ADMIN)
            )
            return ids.scalars().all()

    async def user_is_admin(self, user: User) -> bool:
        roles = await self.get_user_roles(user)
        return Role.ADMIN in roles

    async def user_is_operator(self, user: User) -> bool:
        roles = await self.get_user_roles(user)
        return Role.OPERATOR in roles or Role.ADMIN in roles

    async def user_is_moderator(self, user: User) -> bool:
        roles = await self.get_user_roles(user)
        return Role.MODERATOR in roles or Role.ADMIN in roles

    async def is_admin(self, chat_id: int) -> bool:
        user: User = await self.get_by_id(id_=chat_id)
        if user is None:
            return False
        return await self.user_is_admin(user)

    async def is_operator(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False
        return await self.user_is_operator(user)

    async def is_moderator(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False
        return await self.user_is_moderator(user)

    async def exists(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        return user is not None
