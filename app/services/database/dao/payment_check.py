from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.payment_check import PaymentCheck


class PaymentCheckDAO(BaseDAO[PaymentCheck]):
    def __init__(self, session: AsyncSession):
        super().__init__(PaymentCheck, session)

    async def add(self, payment_check: PaymentCheck) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(payment_check)
        await self._session.commit()

    async def get_payment_checks_to_notify(self) -> Sequence[PaymentCheck]:
        result = await self._session.execute(
            select(PaymentCheck).where(
                or_(
                    PaymentCheck.count_notifications == 0,
                    and_(
                        PaymentCheck.checked.is_(False),
                        datetime.now() - PaymentCheck.last_notification
                        >= timedelta(hours=1),
                    ),
                )
            )
        )
        return result.scalars().all()

    async def get_payment_checks_to_alert(self) -> Sequence[PaymentCheck]:
        result = await self._session.execute(
            select(PaymentCheck)
            .where(PaymentCheck.count_notifications == 3)
            .where(PaymentCheck.alerted.is_(False))
        )
        return result.scalars().all()

    async def make_notified(self, payment_check: PaymentCheck) -> None:
        await self._session.execute(
            update(PaymentCheck)
            .where(PaymentCheck.id == payment_check.id)
            .values(
                last_notification=datetime.now(),
                count_notifications=payment_check.count_notifications + 1,
            )
        )
        await self._session.commit()

    async def make_checked(self, payment_check: PaymentCheck) -> None:
        await self._session.execute(
            update(PaymentCheck)
            .where(PaymentCheck.id == payment_check.id)
            .values(checked=True)
        )
        await self._session.commit()

    async def make_alerted(self, payment_check: PaymentCheck) -> None:
        await self._session.execute(
            update(PaymentCheck)
            .where(PaymentCheck.id == payment_check.id)
            .values(alerted=True)
        )
        await self._session.commit()
