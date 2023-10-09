from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.promocode import PromocodeDAO

from app.services.database.dao.promocode_check import PromocodeCheckDAO
from app.services.database.models.promocode_check import PromocodeCheck


async def create_promocode_check_for_past_week(
    sessionmaker: async_sessionmaker,
) -> None:
    async with sessionmaker() as session:
        promocode_check_dao = PromocodeCheckDAO(session)

        date = datetime.now()
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_check = date
        start_check = end_check - timedelta(weeks=1)
        print(start_check, end_check)
        promocodes = await PromocodeDAO(session).get_between_time(
            start_check, end_check
        )
        await promocode_check_dao.add(
            PromocodeCheck(
                start_check=start_check,
                end_check=end_check,
                count_promocodes=len(promocodes),
            )
        )
