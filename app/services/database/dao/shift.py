from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.shift import CloseShift, OpenShift, Shift


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

    async def get_unnotified(self) -> Sequence[Shift]:
        async with self._session() as session:
            shifts = await session.execute(
                select(Shift).where(Shift.notified == False)  # noqa: E712
            )
            return shifts.scalars().all()

    async def get_monthly_unreported(self) -> Sequence[Shift]:
        async with self._session() as session:
            shifts = await session.execute(
                select(Shift)
                .where(Shift.monthly_reported.is_(False))
                .where(Shift.close_date.is_not(None))
            )
            return shifts.scalars().all()

    async def make_notified(self, shift: Shift):
        async with self._session() as session:
            await session.execute(
                update(Shift).where(Shift.id == shift.id).values(notified=True)
            )
            await session.commit()

    async def make_monthly_reported(self, shift: Shift):
        async with self._session() as session:
            await session.execute(
                update(Shift).where(Shift.id == shift.id).values(monthly_reported=True)
            )
            await session.commit()

    async def is_shift_opened(self) -> bool:
        async with self._session() as session:
            result = await session.execute(
                select(Shift).order_by(Shift.close_date.desc())
            )

            first = result.scalar()

            if first is None:
                return False

            if first.open_date is not None and first.close_date is not None:
                return False

            return True

    async def get_last_shift(self) -> Shift | None:
        async with self._session() as session:
            result = await session.execute(
                select(Shift).order_by(Shift.close_date.desc())
            )
            return result.scalar()

    async def get_last_closed(self) -> Shift:
        async with self._session() as session:
            result = await session.execute(
                select(Shift)
                .where(Shift.close_date.is_not(None))
                .order_by(Shift.close_date.desc())
            )
            return result.scalar()


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

    async def get_unnotified(self) -> Sequence[OpenShift]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(OpenShift).where(OpenShift.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def make_notified(self, shift: OpenShift):
        async with self._session() as session:
            await session.execute(
                update(OpenShift).where(OpenShift.id == shift.id).values(notified=True)
            )
            await session.commit()


class CloseShiftDAO(BaseDAO[CloseShift]):
    def __init__(self, session: async_sessionmaker):
        super().__init__(CloseShift, session)

    async def add_shift(self, shift: CloseShift) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(shift)
            await session.commit()

    async def get_unnotified(self) -> Sequence[CloseShift]:
        async with self._session() as session:
            bonuses = await session.execute(
                select(CloseShift).where(CloseShift.notified == False)  # noqa: E712
            )
            return bonuses.scalars().all()

    async def make_notified(self, shift: CloseShift):
        async with self._session() as session:
            await session.execute(
                update(CloseShift)
                .where(CloseShift.id == shift.id)
                .values(notified=True)
            )
            await session.commit()
