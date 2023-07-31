from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.corporate_report import CorporateReport


class CorporateReportDAO(BaseDAO[CorporateReport]):
    def __init__(self, session: async_sessionmaker):
        super().__init__(CorporateReport, session)

    async def add(self, corporate_report: CorporateReport):
        async with self._session() as session:
            await session.merge(corporate_report)
            await session.commit()

    async def make_reported(self, corporate_report: CorporateReport):
        async with self._session() as session:
            await session.execute(
                update(CorporateReport)
                .where(CorporateReport.id == corporate_report.id)
                .values(reported=True)
            )
            await session.commit()

    async def get_unreported(self) -> list[CorporateReport]:
        async with self._session() as session:
            results = await session.execute(
                select(CorporateReport).where(CorporateReport.reported.is_(False))
            )
            return list(results.scalars().all())
