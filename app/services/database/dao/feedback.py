from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.feedback import Feedback


class FeedbackDAO(BaseDAO):
    def __init__(self, session: async_sessionmaker):
        super().__init__(Feedback, session)

    async def get_by_id(self, id_: str | int) -> Feedback | None:
        return await super().get_by_id(id_)

    async def add_feedback(self, feedback: Feedback):
        async with self._session() as session:
            await session.merge(feedback)
            await session.commit()

    async def get_unnotified(self) -> list[Feedback]:
        async with self._session() as session:
            results = await session.execute(
                select(Feedback)
                .where(Feedback.notified.is_(False))
                .order_by(Feedback.date.asc())
            )
            return list(results.scalars().all())

    async def add_notify_message_id(
        self, feedback: Feedback, chat_id: int, message_id: int
    ):
        new_list = feedback.notify_messages_ids
        new_list.append({"chat_id": chat_id, "message_id": message_id})
        async with self._session() as session:
            await session.execute(
                update(Feedback)
                .where(Feedback.id == feedback.id)
                .values(notify_messages_ids=new_list)
            )
            await session.commit()

    async def make_notified(self, feedback: Feedback):
        async with self._session() as session:
            await session.execute(
                update(Feedback).where(Feedback.id == feedback.id).values(notified=True)
            )
            await session.commit()

    async def make_checked(self, feedback: Feedback):
        async with self._session() as session:
            await session.execute(
                update(Feedback).where(Feedback.id == feedback.id).values(checked=True)
            )
            await session.commit()
