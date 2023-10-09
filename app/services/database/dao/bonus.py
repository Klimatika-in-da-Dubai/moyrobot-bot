from datetime import datetime
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.bonus import Bonus


class BonusDAO(BaseDAO[Bonus]):
    def __init__(self, session: AsyncSession):
        super().__init__(Bonus, session)

    async def add_bonus(self, bonus: Bonus):
        await self._session.merge(bonus)
        await self._session.commit()

    async def get_unnotified(self) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus).where(Bonus.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus)
            .filter(Bonus.date.between(begin, end))
            .where(Bonus.notified == False)  # noqa: E712
        )
        return bonuses.scalars().all()

    async def get_between_time(self, begin: datetime, end: datetime) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus).filter(Bonus.date.between(begin, end))
        )
        return bonuses.scalars().all()

    async def get_unhandled_between_time(
        self, begin: datetime, end: datetime
    ) -> Sequence[Bonus]:
        bonuses = await self._session.execute(
            select(Bonus)
            .where(Bonus.given.is_(None))
            .filter(Bonus.date.between(begin, end))
        )
        return bonuses.scalars().all()

    async def add_notify_message_id(self, bonus: Bonus, chat_id: int, message_id: int):
        new_list = bonus.notify_messages_ids
        new_list.append({"chat_id": chat_id, "message_id": message_id})
        await self._session.execute(
            update(Bonus)
            .where(Bonus.id == bonus.id)
            .values(notify_messages_ids=new_list)
        )
        await self.commit()

    async def delete_notify_messages(self, bonus: Bonus):
        await self._session.execute(
            update(Bonus).where(Bonus.id == bonus.id).values(notify_messages_ids=[])
        )
        await self.commit()

    async def set_given(self, bonus: Bonus, given_value: bool):
        bonus.given = given_value
        await self.commit()

    async def make_notified(self, bonus: Bonus):
        await self._session.execute(
            update(Bonus).where(Bonus.id == bonus.id).values(notified=True)
        )
        await self._session.commit()
