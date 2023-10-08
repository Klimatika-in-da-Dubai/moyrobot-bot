from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.promocode_check import PromocodeCheck


class PromocodeCheckDAO(BaseDAO[PromocodeCheck]):
    def __init__(self, session: AsyncSession):
        super().__init__(PromocodeCheck, session)

    async def add(self, promocode_check: PromocodeCheck) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(promocode_check)
        await self._session.commit()

    async def get_promocode_checks_to_notify(self) -> Sequence[PromocodeCheck]:
        result = await self._session.execute(
            select(PromocodeCheck).where(
                or_(
                    PromocodeCheck.count_notifications == 0,
                    and_(
                        PromocodeCheck.checked.is_(False),
                        datetime.now() - PromocodeCheck.last_notification
                        >= timedelta(hours=1),
                    ),
                )
            )
        )
        return result.scalars().all()

    async def get_promocode_checks_to_alert(self) -> Sequence[PromocodeCheck]:
        result = await self._session.execute(
            select(PromocodeCheck)
            .where(PromocodeCheck.count_notifications == 3)
            .where(PromocodeCheck.alerted.is_(False))
        )
        return result.scalars().all()

    async def make_notified(self, promocode_check: PromocodeCheck) -> None:
        await self._session.execute(
            update(PromocodeCheck)
            .where(PromocodeCheck.id == promocode_check.id)
            .values(
                last_notification=datetime.now(),
                count_notifications=promocode_check.count_notifications + 1,
            )
        )
        await self._session.commit()

    async def make_checked(self, promocode_check: PromocodeCheck) -> None:
        await self._session.execute(
            update(PromocodeCheck)
            .where(PromocodeCheck.id == promocode_check.id)
            .values(checked=True)
        )
        await self._session.commit()

    async def make_alerted(self, promocode_check: PromocodeCheck) -> None:
        await self._session.execute(
            update(PromocodeCheck)
            .where(PromocodeCheck.id == promocode_check.id)
            .values(alerted=True)
        )
        await self._session.commit()
