from datetime import datetime, timedelta
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.consumable_request import (
    Consumable,
    ConsumableRequest,
)


class ConsumableRequestDAO(BaseDAO):
    def __init__(self, session: AsyncSession):
        super().__init__(ConsumableRequest, session)

    async def get_by_id(self, id_: str | int) -> ConsumableRequest | None:
        return await super().get_by_id(id_)

    async def add_consumable_request(self, consumable_request: ConsumableRequest):
        await self._session.merge(consumable_request)
        await self._session.commit()

    async def get_requests_to_notify(
        self, delta_between_notifies: timedelta
    ) -> list[ConsumableRequest]:
        results = await self._session.execute(
            select(ConsumableRequest)
            .where(
                and_(
                    or_(
                        ConsumableRequest.last_notify_timestamp.is_(None),
                        datetime.now() - ConsumableRequest.last_notify_timestamp
                        > delta_between_notifies,
                    ),
                    ConsumableRequest.satisfied.is_(False),
                )
            )
            .order_by(ConsumableRequest.date.asc())
        )
        return list(results.scalars().all())

    async def add_notify_message_id(
        self, consumable_request: ConsumableRequest, chat_id: int, message_id: int
    ):
        new_list = consumable_request.notify_messages_ids
        new_list.append({"chat_id": chat_id, "message_id": message_id})

        await self._session.execute(
            update(ConsumableRequest)
            .where(ConsumableRequest.id == consumable_request.id)
            .values(notify_messages_ids=new_list)
        )
        await self._session.commit()

    async def delete_notify_messages(self, consumable_request: ConsumableRequest):
        await self._session.execute(
            update(ConsumableRequest)
            .where(ConsumableRequest.id == consumable_request.id)
            .values(notify_messages_ids=[])
        )
        await self._session.commit()

    async def make_notified(self, consumable_request: ConsumableRequest):
        await self._session.execute(
            update(ConsumableRequest)
            .where(ConsumableRequest.id == consumable_request.id)
            .values(last_notify_timestamp=datetime.now())
        )
        await self._session.commit()

    async def make_satisfied(self, consumable_request: ConsumableRequest):
        await self._session.execute(
            update(ConsumableRequest)
            .where(ConsumableRequest.id == consumable_request.id)
            .values(satisfied=True)
        )
        await self._session.commit()

    async def get_last_consumable_request(
        self, consumable: Consumable
    ) -> ConsumableRequest | None:
        orders = await self._session.execute(
            select(ConsumableRequest)
            .where(ConsumableRequest.consumable == consumable)
            .order_by(ConsumableRequest.date.desc())
        )

        return orders.scalar()
