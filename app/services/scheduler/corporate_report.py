from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.database.dao.corporate_report import CorporateReportDAO
from app.services.database.models.corporate_report import CorporateReport


async def create_corporate_report_for_past_month(session: async_sessionmaker):
    corporate_report_dao = CorporateReportDAO(session)

    date = datetime.now()
    date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = date - relativedelta(months=1)
    end = date

    await corporate_report_dao.add(CorporateReport(start=start, end=end))
