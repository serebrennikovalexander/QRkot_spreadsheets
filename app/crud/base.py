from datetime import datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def save_object(
        self,
        db_obj,
        session: AsyncSession,
    ):
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def close_object_use_dict_data(
            self,
            obj_in,
            obj_dict: dict[str, Any],
            session: AsyncSession,
    ):
        # Закрываем объект используя словарь из данных POST-запроса
        obj_dict["invested_amount"] = (
            obj_in.full_amount
        )
        obj_dict["fully_invested"] = True
        obj_dict["close_date"] = datetime.utcnow()

    async def close_object_use_db_data(
            self,
            db_obj,
            session: AsyncSession,
    ):
        # Закрываем объект используя объект из базы данных
        db_obj.invested_amount = db_obj.full_amount
        db_obj.fully_invested = True
        db_obj.close_date = datetime.utcnow()
