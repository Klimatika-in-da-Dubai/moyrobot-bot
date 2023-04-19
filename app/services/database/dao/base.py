from typing import Sequence, TypeVar, Type, Generic

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from app.services.database.base import Base

Model = TypeVar("Model", Base, Base)


class BaseDAO(Generic[Model]):
    """ORM queries for abstract table"""

    def __init__(self, model: Type[Model], session: async_sessionmaker[AsyncSession]):
        """
        :param model:
        :param session:
        """

        self._model = model
        self._session = session

    async def get_all(self) -> Sequence[Model]:
        """
        :return: List of models.
        """

        async with self._session() as session:
            result = await session.execute(select(self._model))
            return result.scalars().all()

    async def get_by_id(self, id_: str | int) -> Model | None:
        """
        :param id_: input id
        :return:
        """

        async with self._session() as session:
            result = await session.execute(
                select(self._model).where(self._model.id == id_)
            )
            return result.scalars().first()

    async def delete_all(self) -> None:
        """
        Clear table
        :return:
        """

        async with self._session() as session:
            await session.execute(delete(self._model))

    async def count(self) -> int:
        """
        :return: count of model.
        """

        async with self._session() as session:
            result = await session.execute(select(func.count(self._model.id)))
            return result.scalar_one()

    async def commit(self) -> None:
        """
        Commit re-impl
        :return:
        """

        async with self._session() as session:
            await session.commit()
