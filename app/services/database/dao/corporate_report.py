from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.corporate_report import CorporateReport


class CorporateReportDAO(BaseDAO[CorporateReport]):
    def __init__(self, session: AsyncSession):
        super().__init__(CorporateReport, session)

    async def add(self, corporate_report: CorporateReport):
        await self._session.merge(corporate_report)
        await self._session.commit()

    async def make_reported(self, corporate_report: CorporateReport):
        await self._session.execute(
            update(CorporateReport)
            .where(CorporateReport.id == corporate_report.id)
            .values(reported=True)
        )
        await self._session.commit()

    async def get_unreported(self) -> list[CorporateReport]:
        results = await self._session.execute(
            select(CorporateReport).where(CorporateReport.reported.is_(False))
        )
        return list(results.scalars().all())
