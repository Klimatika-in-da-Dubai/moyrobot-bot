from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.bonus import BonusDAO
from app.services.database.dao.bonus_check import BonusCheckDAO
from app.services.database.models.bonus_check import BonusCheck


async def create_bonus_check_for_past_week(session: async_sessionmaker) -> None:
    bonus_check_dao = BonusCheckDAO(session)

    date = datetime.now()
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_check = date
    start_check = end_check - timedelta(weeks=1)
    print(start_check, end_check)

    bonuses = await BonusDAO(session).get_between_time(start_check, end_check)

    await bonus_check_dao.add(
        BonusCheck(
            start_check=start_check,
            end_check=end_check,
            count_bonuses=len(bonuses),
        )
    )
