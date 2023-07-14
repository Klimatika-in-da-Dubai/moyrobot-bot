from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.payment_check import PaymentCheck


class PaymentCheckDAO(BaseDAO[PaymentCheck]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(PaymentCheck, session)

    async def add(self, payment_check: PaymentCheck) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        async with self._session() as session:
            await session.merge(payment_check)
            await session.commit()

    async def get_payment_checks_to_notify(self) -> Sequence[PaymentCheck]:
        async with self._session() as session:
            result = await session.execute(
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
        async with self._session() as session:
            result = await session.execute(
                select(PaymentCheck)
                .where(PaymentCheck.count_notifications == 3)
                .where(PaymentCheck.alerted.is_(False))
            )
            return result.scalars().all()

    async def make_notified(self, payment_check: PaymentCheck) -> None:
        async with self._session() as session:
            await session.execute(
                update(PaymentCheck)
                .where(PaymentCheck.id == payment_check.id)
                .values(
                    last_notification=datetime.now(),
                    count_notifications=payment_check.count_notifications + 1,
                )
            )
            await session.commit()

    async def make_checked(self, payment_check: PaymentCheck) -> None:
        async with self._session() as session:
            await session.execute(
                update(PaymentCheck)
                .where(PaymentCheck.id == payment_check.id)
                .values(checked=True)
            )
            await session.commit()

    async def make_alerted(self, payment_check: PaymentCheck) -> None:
        async with self._session() as session:
            await session.execute(
                update(PaymentCheck)
                .where(PaymentCheck.id == payment_check.id)
                .values(alerted=True)
            )
            await session.commit()
