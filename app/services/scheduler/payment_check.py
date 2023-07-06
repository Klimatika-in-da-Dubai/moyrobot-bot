from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.manual_start import ManualStartDAO

from app.services.database.dao.payment_check import PaymentCheckDAO
from app.services.database.models.manual_start import ManualStartType
from app.services.database.models.payment_check import PaymentCheck
from app.services.database.models.utils import PaymentMethod


async def create_payment_check_for_past_day(session: async_sessionmaker) -> None:
    payment_check_dao = PaymentCheckDAO(session)
    manual_start_dao = ManualStartDAO(session)

    date = datetime.now()
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    start_check = date - timedelta(days=1)
    end_check = date

    manual_starts = await manual_start_dao.get_typed_between_time(
        ManualStartType.PAID, start_check, end_check
    )
    card_manual_starts = list(
        filter(lambda x: x.payment_method is PaymentMethod.CARD, manual_starts)
    )

    await payment_check_dao.add(
        PaymentCheck(
            start_check=start_check,
            end_check=end_check,
            count_manual_starts=len(card_manual_starts),
        )
    )
