from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, join
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

    async def get_user_roles(self, user: User) -> list[Role]:
        async with self._session() as session:
            roles = await session.execute(
                select(UserRole.role).join(User).where(self._model.id == user.id)
            )
            roles_list = roles.scalars().all()
            return roles_list

    async def user_is_admin(self, user: User) -> bool:
        roles = await self.get_user_roles(user)
        return Role.ADMIN in roles


async def is_admin(chat_id: int, session) -> bool:
    userdao = UserDAO(session=session)
    user: User = await userdao.get_by_id(id_=chat_id)

    if user is None:
        return False

    return await userdao.user_is_admin(user)
