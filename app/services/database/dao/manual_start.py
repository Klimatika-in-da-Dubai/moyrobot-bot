import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.manual_start import (
    ManualStartType,
    ManualStart,
    TestManualStart,
    ServiceManualStart,
    RewashManualStart,
    PaidManualStart,
)


class ManualStartDAO(BaseDAO[ManualStart]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(ManualStart, session)

    async def add_manual_start(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.merge(manual_start)
            await session.commit()

    async def update_manual_start_mode(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.execute(
                update(ManualStart)
                .where(ManualStart.id == manual_start.id)
                .values(mode=manual_start.mode)
            )
            await session.commit()

    async def get_n_unreported_manual_starts(self, n: int) -> Sequence[ManualStart]:
        async with self._session() as session:
            manual_starts = await session.execute(
                select(ManualStart)
                .filter_by(reported=False)
                .order_by(ManualStart.date.asc())
                .limit(n)
            )
            return manual_starts.scalars().all()

    async def get_unreminded(self, delay: datetime.timedelta) -> Sequence[ManualStart]:
        async with self._session() as session:
            manual_starts = await session.execute(
                select(ManualStart)
                .where(ManualStart.reported == False)  # noqa: E712
                .where(ManualStart.report_reminded == False)  # noqa: E712
                .where((datetime.datetime.now() - ManualStart.date) > delay)
            )
            return manual_starts.scalars().all()

    async def get_unalerted(self, delay: datetime.timedelta) -> Sequence[ManualStart]:
        async with self._session() as session:
            manual_starts = await session.execute(
                select(ManualStart)
                .where(ManualStart.reported == False)  # noqa: E712
                .where(ManualStart.report_alerted == False)  # noqa: E712
                .where((datetime.datetime.now() - ManualStart.date) > delay)
            )

            return manual_starts.scalars().all()

    async def get_unnotified(self) -> Sequence[ManualStart]:
        async with self._session() as session:
            manual_starts = await session.execute(
                select(ManualStart)
                .where(ManualStart.reported == True)  # noqa: E712
                .where(ManualStart.notified == False)  # noqa: E712
            )

            return manual_starts.scalars().all()

    async def make_report_reminded(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.execute(
                update(ManualStart)
                .where(ManualStart.id == manual_start.id)
                .values(report_reminded=True)
            )
            await session.commit()

    async def make_report_alerted(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.execute(
                update(ManualStart)
                .where(ManualStart.id == manual_start.id)
                .values(report_alerted=True)
            )
            await session.commit()

    async def make_notified(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.execute(
                update(ManualStart)
                .where(ManualStart.id == manual_start.id)
                .values(notified=True)
            )
            await session.commit()

    async def get_typed_manual_start(
        self, manual_start_id: str, type: ManualStartType
    ) -> TestManualStart | ServiceManualStart | RewashManualStart | PaidManualStart:
        manual_start_table = self._match_manual_start_type(type)
        async with self._session() as session:
            manual_start = await session.execute(
                select(manual_start_table).where(
                    manual_start_table.id == manual_start_id
                )
            )
            return manual_start.scalars().first()

    def _match_manual_start_type(self, type: ManualStartType):
        match type:
            case ManualStartType.TEST:
                return TestManualStart
            case ManualStartType.SERVICE:
                return ServiceManualStart
            case ManualStartType.REWASH:
                return RewashManualStart
            case ManualStartType.PAID:
                return PaidManualStart

    async def report_typed_manual_start(
        self,
        typed_manual_start: TestManualStart
        | ServiceManualStart
        | RewashManualStart
        | PaidManualStart,
        type: ManualStartType,
    ):
        async with self._session() as session:
            await session.execute(
                update(ManualStart)
                .where(ManualStart.id == typed_manual_start.id)
                .values(reported=True, type=type)
            )
            await session.merge(typed_manual_start)
            await session.commit()
