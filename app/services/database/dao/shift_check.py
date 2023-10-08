from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.shift_check import ShiftCheck


class ShiftCheckDAO(BaseDAO[ShiftCheck]):
    def __init__(self, session: AsyncSession):
        super().__init__(ShiftCheck, session)

    async def add(self, shift_check: ShiftCheck) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(shift_check)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[ShiftCheck]:
        shift_checks = await self._session.execute(
            select(ShiftCheck).where(ShiftCheck.notified == False)  # noqa: E712
        )
        return shift_checks.scalars().all()

    async def get_by_id(self, id_: str | int) -> ShiftCheck | None:
        return await super().get_by_id(id_)

    async def make_notified(self, shift_check: ShiftCheck):
        await self._session.execute(
            update(ShiftCheck)
            .where(ShiftCheck.id == shift_check.id)
            .values(notified=True)
        )
        await self._session.commit()
