from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.feedback import Feedback


class FeedbackDAO(BaseDAO):
    def __init__(self, session: async_sessionmaker):
        super().__init__(Feedback, session)

    async def add_feedback(self, feedback: Feedback):
        async with self._session() as session:
            await session.merge(feedback)
            await session.commit()
