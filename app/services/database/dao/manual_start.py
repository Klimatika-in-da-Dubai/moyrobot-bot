from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from app.services.database.dao.base import BaseDAO
from app.services.database.models.manual_start import (
    ManualStartType,
    ManualStart,
    TestManualStart,
    ServiceManualStart,
    RewashManualStart,
    PaidManualStart,
)


class ManualStartDAO(BaseDAO):
    def __init__(self, session: async_sessionmaker):
        super().__init__(ManualStart, session)

    async def add_manual_start(self, manual_start: ManualStart):
        async with self._session() as session:
            await session.merge(manual_start)
            await session.commit()

    async def get_n_unreported_manual_starts(self, n: int) -> list[ManualStart]:
        async with self._session() as session:
            manual_starts = await session.execute(
                select(ManualStart)
                .filter_by(reported=False)
                .order_by(ManualStart.date.asc())
                .limit(n)
            )
            return manual_starts.scalars().all()
