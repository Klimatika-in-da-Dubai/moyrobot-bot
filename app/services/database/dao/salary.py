from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.database.dao.base import BaseDAO
from app.services.database.models.salary import Salary


class SalaryDAO(BaseDAO[Salary]):
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        super().__init__(Salary, session)

    async def add_salary(self, salary: Salary):
        async with self._session() as session:
            await session.merge(salary)
            await session.commit()
