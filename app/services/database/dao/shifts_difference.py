from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.shifts_difference import ShiftsDifference


class ShiftsDifferenceDAO(BaseDAO[ShiftsDifference]):
    def __init__(self, session: AsyncSession):
        super().__init__(ShiftsDifference, session)

    async def add(self, shifts_difference: ShiftsDifference) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(shifts_difference)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[ShiftsDifference]:
        shift_checks = await self._session.execute(
            select(ShiftsDifference).where(
                ShiftsDifference.notified == False  # noqa: E712
            )
        )
        return shift_checks.scalars().all()

    async def get_by_ids(
        self, closed_shift_id: int, opened_shift_id: int
    ) -> ShiftsDifference:
        shift_difference = await self._session.execute(
            select(ShiftsDifference)
            .where(ShiftsDifference.closed_shift_id == closed_shift_id)
            .where(ShiftsDifference.opened_shift_id == opened_shift_id)
        )
        return shift_difference.scalar()

    async def make_notified(self, shifts_difference: ShiftsDifference):
        await self._session.execute(
            update(ShiftsDifference)
            .where(
                ShiftsDifference.closed_shift_id == shifts_difference.closed_shift_id
            )
            .where(
                ShiftsDifference.opened_shift_id == shifts_difference.opened_shift_id
            )
            .values(notified=True)
        )
        await self._session.commit()
