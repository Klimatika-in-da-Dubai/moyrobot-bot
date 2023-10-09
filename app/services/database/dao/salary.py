from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.base import BaseDAO
from app.services.database.models.salary import Salary


class SalaryDAO(BaseDAO[Salary]):
    def __init__(self, session: AsyncSession):
        super().__init__(Salary, session)

    async def add_salary(self, salary: Salary):
        await self._session.merge(salary)
        await self._session.commit()
