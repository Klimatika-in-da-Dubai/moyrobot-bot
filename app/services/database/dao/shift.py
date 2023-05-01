from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.shift import OpenShift, Shift


class ShiftDAO(BaseDAO[Shift]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Shift, session)

    async def add_shift(self, shift: Shift) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(shift)
            await session.commit()

    async def is_shift_opened(self) -> bool:
        async with self._session() as session:
            result = await session.execute(
                select(Shift).order_by(Shift.close_date.desc())
            )

            first = result.first()

            if first is None:
                return False

            if first.close_date is None:
                return False

            return True


class OpenShiftDAO(BaseDAO[OpenShift]):
    def __init__(self, session: async_sessionmaker):
        super().__init__(OpenShift, session)

    async def add_shift(self, shift: OpenShift) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(shift)
            await session.commit()
