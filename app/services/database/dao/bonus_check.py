from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.bonus_check import BonusCheck


class BonusCheckDAO(BaseDAO[BonusCheck]):
    def __init__(self, session: AsyncSession):
        super().__init__(BonusCheck, session)

    async def add(self, bonus_check: BonusCheck) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(bonus_check)
        await self._session.commit()

    async def get_bonus_checks_to_notify(
        self, delta: timedelta
    ) -> Sequence[BonusCheck]:
        result = await self._session.execute(
            select(BonusCheck).where(
                or_(
                    BonusCheck.count_notifications == 0,
                    and_(
                        BonusCheck.checked.is_(other=False),
                        datetime.now() - BonusCheck.last_notification >= delta,
                    ),
                )
            )
        )
        return result.scalars().all()

    async def get_bonus_checks_to_alert(self) -> Sequence[BonusCheck]:
        result = await self._session.execute(
            select(BonusCheck)
            .where(BonusCheck.count_notifications == 3)
            .where(BonusCheck.alerted.is_(False))
        )
        return result.scalars().all()

    async def add_notify_message_id(
        self, bonus_check: BonusCheck, chat_id: int, message_id: int
    ):
        new_list = bonus_check.notify_messages_ids
        new_list.append({"chat_id": chat_id, "message_id": message_id})
        await self._session.execute(
            update(BonusCheck)
            .where(BonusCheck.id == bonus_check.id)
            .values(notify_messages_ids=new_list)
        )
        await self.commit()

    async def delete_notify_messages(self, bonus_check: BonusCheck):
        await self._session.execute(
            update(BonusCheck)
            .where(BonusCheck.id == bonus_check.id)
            .values(notify_messages_ids=[])
        )
        await self.commit()

    async def make_notified(self, bonus_check: BonusCheck) -> None:
        await self._session.execute(
            update(BonusCheck)
            .where(BonusCheck.id == bonus_check.id)
            .values(
                last_notification=datetime.now(),
                count_notifications=bonus_check.count_notifications + 1,
            )
        )
        await self._session.commit()

    async def make_checked(self, bonus_check: BonusCheck) -> None:
        await self._session.execute(
            update(BonusCheck)
            .where(BonusCheck.id == bonus_check.id)
            .values(checked=True)
        )
        await self._session.commit()

    async def make_alerted(self, bonus_check: BonusCheck) -> None:
        await self._session.execute(
            update(BonusCheck)
            .where(BonusCheck.id == bonus_check.id)
            .values(alerted=True)
        )
        await self._session.commit()
