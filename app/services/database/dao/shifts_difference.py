from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.shifts_difference import ShiftsDifference


class ShiftsDifferenceDAO(BaseDAO[ShiftsDifference]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(ShiftsDifference, session)

    async def add(self, shifts_difference: ShiftsDifference) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(shifts_difference)
            await session.commit()

    async def get_unnotified(self) -> Sequence[ShiftsDifference]:
        async with self._session() as session:
            shift_checks = await session.execute(
                select(ShiftsDifference).where(
                    ShiftsDifference.notified == False  # noqa: E712
                )
            )
            return shift_checks.scalars().all()

    async def get_by_ids(
        self, closed_shift_id: int, opened_shift_id: int
    ) -> ShiftsDifference:
        async with self._session() as session:
            shift_difference = await session.execute(
                select(ShiftsDifference)
                .where(ShiftsDifference.closed_shift_id == closed_shift_id)
                .where(ShiftsDifference.opened_shift_id == opened_shift_id)
            )
            return shift_difference.scalar()

    async def make_notified(self, shifts_difference: ShiftsDifference):
        async with self._session() as session:
            await session.execute(
                update(ShiftsDifference)
                .where(
                    ShiftsDifference.closed_shift_id
                    == shifts_difference.closed_shift_id
                )
                .where(
                    ShiftsDifference.opened_shift_id
                    == shifts_difference.opened_shift_id
                )
                .values(notified=True)
            )
            await session.commit()
