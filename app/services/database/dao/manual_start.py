import datetime
from typing import Sequence, assert_never
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.manual_start import (
    CorporateManualStart,
    ManualStartType,
    ManualStart,
    TestManualStart,
    ServiceManualStart,
    RewashManualStart,
    PaidManualStart,
)


class ManualStartDAO(BaseDAO[ManualStart]):
    def __init__(self, session: AsyncSession):
        super().__init__(ManualStart, session)

    async def get_by_id(self, id_: str) -> ManualStart | None:
        return await super().get_by_id(id_)

    async def add_manual_start(self, manual_start: ManualStart):
        await self._session.merge(manual_start)
        await self._session.commit()

    async def update_manual_start_mode(self, manual_start: ManualStart):
        await self._session.execute(
            update(ManualStart)
            .where(ManualStart.id == manual_start.id)
            .values(mode=manual_start.mode)
        )
        await self._session.commit()

    async def get_n_unreported_manual_starts(self, n: int) -> Sequence[ManualStart]:
        manual_starts = await self._session.execute(
            select(ManualStart)
            .filter_by(reported=False)
            .order_by(ManualStart.date.asc())
            .limit(n)
        )
        return manual_starts.scalars().all()

    async def get_unreminded(self, delay: datetime.timedelta) -> Sequence[ManualStart]:
        manual_starts = await self._session.execute(
            select(ManualStart)
            .where(ManualStart.reported == False)  # noqa: E712
            .where(ManualStart.report_reminded == False)  # noqa: E712
            .where((datetime.datetime.now() - ManualStart.date) > delay)
        )
        return manual_starts.scalars().all()

    async def get_unalerted(self, delay: datetime.timedelta) -> Sequence[ManualStart]:
        manual_starts = await self._session.execute(
            select(ManualStart)
            .where(ManualStart.reported == False)  # noqa: E712
            .where(ManualStart.report_alerted == False)  # noqa: E712
            .where((datetime.datetime.now() - ManualStart.date) > delay)
        )

        return manual_starts.scalars().all()

    async def get_alerted_between_time(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> Sequence[ManualStart]:
        manual_starts = await self._session.execute(
            select(ManualStart)
            .where(ManualStart.report_alerted.is_(True))
            .filter(ManualStart.date.between(begin, end))
        )

        return manual_starts.scalars().all()

    async def get_unnotified(self) -> Sequence[ManualStart]:
        manual_starts = await self._session.execute(
            select(ManualStart)
            .where(ManualStart.reported == True)  # noqa: E712
            .where(
                or_(
                    ManualStart.mode.is_not(None),
                    datetime.datetime.now() - ManualStart.date
                    > datetime.timedelta(seconds=15 * 60),
                )
            )  # noqa: E711
            .where(ManualStart.notified == False)  # noqa: E712
        )

        return manual_starts.scalars().all()

    async def make_report_reminded(self, manual_start: ManualStart):
        await self._session.execute(
            update(ManualStart)
            .where(ManualStart.id == manual_start.id)
            .values(report_reminded=True)
        )
        await self._session.commit()

    async def make_report_alerted(self, manual_start: ManualStart):
        await self._session.execute(
            update(ManualStart)
            .where(ManualStart.id == manual_start.id)
            .values(report_alerted=True)
        )
        await self._session.commit()

    async def make_notified(self, manual_start: ManualStart):
        await self._session.execute(
            update(ManualStart)
            .where(ManualStart.id == manual_start.id)
            .values(notified=True)
        )
        await self._session.commit()

    async def get_typed_manual_start(
        self, manual_start_id: str, type: ManualStartType
    ) -> ManualStart:
        manual_start_table = self._match_manual_start_type(type)

        manual_start = await self._session.execute(
            select(manual_start_table).where(manual_start_table.id == manual_start_id)
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
            case ManualStartType.CORPORATE:
                return CorporateManualStart
            case _ as never:
                assert_never(never)

    async def report_typed_manual_start(
        self,
        typed_manual_start: TestManualStart
        | ServiceManualStart
        | RewashManualStart
        | PaidManualStart
        | CorporateManualStart,
        type: ManualStartType,
    ):
        await self._session.execute(
            update(ManualStart)
            .where(ManualStart.id == typed_manual_start.id)
            .values(reported=True, type=type)
        )
        await self._session.merge(typed_manual_start)
        await self._session.commit()

    async def get_typed_between_time(
        self, type: ManualStartType, begin: datetime.datetime, end: datetime.datetime
    ):
        typed_manual_start_table = self._match_manual_start_type(type)
        result = await self._session.execute(
            select(typed_manual_start_table)
            .join(ManualStart)
            .where(ManualStart.type == type)
            .where(ManualStart.date.between(begin, end))
            .order_by(ManualStart.date)
        )

        return result.scalars().all()
