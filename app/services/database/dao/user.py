from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import delete, select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.mailing import Mailing
from app.services.database.models.salary import Salary
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

    async def delete_user(self, user: User) -> None:
        async with self._session() as session:
            await session.execute(
                update(User).where(User.id == user.id).values(active=False)
            )
            await session.commit()

    async def get_all_active(self) -> Sequence[User]:
        """
        :return: List of models.
        """
        async with self._session() as session:
            result = await session.execute(select(User).where(User.active.is_(True)))
            return result.scalars().all()

    async def add_user_with_roles(self, user: User, user_roles: list[UserRole]):
        await self.add_user(user)

        async with self._session() as session:
            for user_role in user_roles:
                await session.merge(user_role)

            await session.commit()

    async def update_user_roles(self, user: User, user_roles: list[UserRole]):
        async with self._session() as session:
            await session.execute(delete(UserRole).where(UserRole.id == user.id))

            for role in user_roles:
                await session.merge(role)

            await session.commit()

    async def get_user_roles(self, user: User) -> list[Role]:
        async with self._session() as session:
            roles = await session.execute(
                select(UserRole.role).join(User).where(self._model.id == user.id)
            )
            roles_list = roles.scalars().all()
            return list(roles_list)

    async def get_salary(self, user: User) -> int:
        async with self._session() as session:
            result = await session.execute(
                select(Salary.salary).where(Salary.user_id == user.id)
            )

            return result.scalar()  # type: ignore

    async def get_operators(self) -> list[User]:
        async with self._session() as session:
            users = await session.execute(
                select(User).join(UserRole).where(UserRole.role == Role.OPERATOR)
            )
            return list(users.scalars().all())

    async def get_user_name_by_id(self, chat_id: int) -> str:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            raise RuntimeError("No user with id %s", chat_id)
        return user.name

    async def is_admin(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False
        if user.active is False:
            return False
        roles = await self.get_user_roles(user)
        return Role.ADMIN in roles

    async def is_operator(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False

        if user.active is False:
            return False

        roles = await self.get_user_roles(user)
        return (
            Role.OPERATOR in roles or Role.ADMIN in roles or Role.WORK_ACCOUNT in roles
        )

    async def is_moderator(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False
        if user.active is False:
            return False

        roles = await self.get_user_roles(user)
        return Role.MODERATOR in roles or Role.ADMIN in roles

    async def is_work_account(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        if user is None:
            return False

        if user.active is False:
            return False

        roles = await self.get_user_roles(user)
        return Role.WORK_ACCOUNT in roles

    async def exists(self, chat_id: int) -> bool:
        user = await self.get_by_id(id_=chat_id)
        return user is not None and user.active is True
