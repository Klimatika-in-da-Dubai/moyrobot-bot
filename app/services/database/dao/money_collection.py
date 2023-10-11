import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.services.database.dao.base import BaseDAO
from app.services.database.models.money_collection import MoneyCollection


class MoneyCollectionDAO(BaseDAO[MoneyCollection]):
    def __init__(self, session: AsyncSession):
        super().__init__(MoneyCollection, session)

    async def add_money_collection(self, money_collection: MoneyCollection):
        await self._session.merge(money_collection)
        await self._session.commit()

    async def get_money_collection_between_time(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> Sequence[MoneyCollection]:
        collections = await self._session.execute(
            select(MoneyCollection).filter(MoneyCollection.date.between(begin, end))
        )
        return collections.scalars().all()

    async def get_unnotified(self) -> Sequence[MoneyCollection]:
        collections = await self._session.execute(
            select(MoneyCollection).where(MoneyCollection.notified.is_(False))
        )
        return collections.scalars().all()

    async def get_unnotified_between_time(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> Sequence[MoneyCollection]:
        collections = await self._session.execute(
            select(MoneyCollection)
            .filter(MoneyCollection.date.between(begin, end))
            .where(MoneyCollection.notified == False)  # noqa: E712
        )
        return collections.scalars().all()

    async def make_notified(self, money_collection: MoneyCollection):
        await self._session.execute(
            update(MoneyCollection)
            .where(MoneyCollection.id == money_collection.id)
            .values(notified=True)
        )
        await self._session.commit()
