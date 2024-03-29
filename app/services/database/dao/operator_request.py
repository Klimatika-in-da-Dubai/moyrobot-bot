from datetime import datetime, timedelta
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.operator_request import OperatorRequest


class OperatorRequestDAO(BaseDAO):
    def __init__(self, session: AsyncSession):
        super().__init__(OperatorRequest, session)

    async def get_by_id(self, id_: str | int) -> OperatorRequest | None:
        return await super().get_by_id(id_)

    async def add_operator_request(self, operator_request: OperatorRequest):
        await self._session.merge(operator_request)
        await self._session.commit()

    async def get_requests_to_notify(
        self, delta_between_notifies: timedelta
    ) -> list[OperatorRequest]:
        results = await self._session.execute(
            select(OperatorRequest)
            .where(
                and_(
                    or_(
                        OperatorRequest.last_notify_timestamp.is_(None),
                        datetime.now() - OperatorRequest.last_notify_timestamp
                        > delta_between_notifies,
                    ),
                    OperatorRequest.satisfied.is_(False),
                )
            )
            .order_by(OperatorRequest.date.asc())
        )
        return list(results.scalars().all())

    async def add_notify_message_id(
        self, operator_request: OperatorRequest, chat_id: int, message_id: int
    ):
        new_list = operator_request.notify_messages_ids
        new_list.append({"chat_id": chat_id, "message_id": message_id})

        await self._session.execute(
            update(OperatorRequest)
            .where(OperatorRequest.id == operator_request.id)
            .values(notify_messages_ids=new_list)
        )
        await self._session.commit()

    async def make_notified(self, operator_request: OperatorRequest):
        await self._session.execute(
            update(OperatorRequest)
            .where(OperatorRequest.id == operator_request.id)
            .values(last_notify_timestamp=datetime.now())
        )
        await self._session.commit()

    async def make_satisfied(self, operator_request: OperatorRequest):
        await self._session.execute(
            update(OperatorRequest)
            .where(OperatorRequest.id == operator_request.id)
            .values(satisfied=True)
        )
        await self._session.commit()
