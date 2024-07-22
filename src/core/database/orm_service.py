from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, func, select, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from .filtering import BaseFilterModel
from .types import ConvertibleToWhere, Data, Where


T = TypeVar('T')


class BaseORMService:
    BASE_MODEL: Any = ...

    async def get_many(
        self,
        session: AsyncSession,
        *,
        where: ConvertibleToWhere | None = None,
    ):
        """
        Order by 'created_at'.
        """

        query = select(
            self.BASE_MODEL,
            func.count(self.BASE_MODEL.id).over().label("total_items")
        ).order_by(
            self.BASE_MODEL.created_at.desc()
        )

        query = self.apply_where_to_query(query, where)

        result = await session.execute(query)
        rows = result.fetchall()

        return rows

    async def get_by_id(self, id: UUID, session: AsyncSession, *, throw_not_found: bool = True):
        query = await session.execute(select(self.BASE_MODEL).where(self.BASE_MODEL.id == id))
        result = query.fetchone()

        if result is None:
            if throw_not_found:
                raise Exception("Not found")
            return None

        obj = result[0]
        return obj

    async def update_instance_fields(
        self,
        instance: T,
        data: Data,
        *,
        session: AsyncSession = None,
        save: bool = False
    ) -> T:
        """
        Can automatically save updates, with provided session and save.
        """
        data = self._parse_data(data)

        for key, value in data.items():
            setattr(instance, key, value)

        if save:
            await self.save_and_refresh(instance, session)

        return instance

    async def save_and_refresh(self, instance, session: AsyncSession):
        session.add(instance)
        await session.commit()
        await session.refresh(instance)

    async def delete_by_id(self, id: UUID, session: AsyncSession):
        await session.execute(delete(self.BASE_MODEL).where(self.BASE_MODEL.id == id))
        await session.commit()

    def apply_where_to_query(self, query: T, where: ConvertibleToWhere | None) -> T:
        where = self.__build_where(where)

        return query.where(where)

    def _parse_data(self, data: Data) -> dict:
        if isinstance(data, dict):
            return data

        if isinstance(data, BaseModel):
            return data.model_dump()

        raise ValueError(f"Invalid data type: {type(data)}. Expected dict or BaseModel.")

    def __build_where(self, where: ConvertibleToWhere | None, *, use_filter: bool = True) -> Where:
        """
        Convert to where statement.
        """

        where = self.__filter_where(where) if use_filter else where

        if isinstance(where, list):
            if len(where):
                return and_(*[self.__build_where(el, use_filter=False) for el in where])

            return true()

        if isinstance(where, BaseFilterModel):
            return self.__build_where(where.to_where_statement(), use_filter=False)

        return where

    def __filter_where(self, where: ConvertibleToWhere) -> ConvertibleToWhere:
        """
        Replace 'None' and 'True' expressions on true()
        """

        if isinstance(where, list):
            return [self.__filter_where(el) for el in where]

        if isinstance(where, BaseFilterModel):
            return self.__filter_where(where.to_where_statement())

        if where is None or where is True:
            return true()

        return where
