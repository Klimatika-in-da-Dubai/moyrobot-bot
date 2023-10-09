from operator import and_
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.salary import Salary
from app.services.database.models.user import Role, User, UserPincode, UserRole


class UserDAO(BaseDAO[User]):
    """ORM queries for users table"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def add_user(self, user: User) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(user)
        await self._session.commit()

    async def delete_user(self, user: User) -> None:
        await self._session.execute(
            update(User).where(User.id == user.id).values(active=False)
        )
        await self._session.commit()

    async def get_all_active(self) -> Sequence[User]:
        """
        :return: List of models.
        """

        result = await self._session.execute(select(User).where(User.active.is_(True)))
        return result.scalars().all()

    async def add_user_with_roles(self, user: User, user_roles: list[UserRole]):
        await self.add_user(user)

        for user_role in user_roles:
            await self._session.merge(user_role)

        await self._session.commit()

    async def update_user_roles(self, user: User, user_roles: list[UserRole]):
        await self._session.execute(delete(UserRole).where(UserRole.id == user.id))

        for role in user_roles:
            await self._session.merge(role)

        await self._session.commit()

    async def get_user_roles(self, user: User) -> list[Role]:
        roles = await self._session.execute(
            select(UserRole.role).join(User).where(self._model.id == user.id)
        )
        roles_list = roles.scalars().all()
        return list(roles_list)

    async def get_salary(self, user: User) -> int:
        result = await self._session.execute(
            select(Salary.salary).where(Salary.user_id == user.id)
        )

        return result.scalar()  # type: ignore

    async def set_pincode(self, user_id: int, pincode: str):
        pincode = UserPincode(id=user_id, pincode=pincode)

        await self._session.merge(pincode)
        await self._session.commit()

    async def get_pincode(self, user_id: int) -> Optional[str]:
        result = await self._session.execute(
            select(UserPincode.pincode).where(UserPincode.id == user_id)
        )
        return result.scalar()

    async def get_operators(self) -> list[User]:
        users = await self._session.execute(
            select(User)
            .join(UserRole)
            .where(and_(UserRole.role == Role.OPERATOR, User.active.is_(True)))
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
