from datetime import datetime, timedelta
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject

SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60


class CRUDCharityProject(CRUDBase):

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

        if db_obj.full_amount == db_obj.invested_amount:
            db_obj.fully_invested = True
            db_obj.close_date = datetime.utcnow()

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_open_charity_project(
        self,
        session: AsyncSession,
    ):
        """Функция для получения открытого проекта."""
        db_charity_project = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested == 0)
        )

        return db_charity_project.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[dict[str, str]]:
        """
        Функция для получения списка со всеми
        закрытыми проектами. Список отсортировани по
        количесвту времени, которое понадобилось на сбор
        средств, - от меньшего к большему"""

        # В запрсое получаем время потраченное на сбор средств
        # в секундах
        stmt = (
            select(
                CharityProject.name,
                CharityProject.description,
                (
                    func.strftime("%s", CharityProject.close_date) -
                    func.strftime("%s", CharityProject.create_date)
                ).label("time_diff"),
            )
            .where(CharityProject.fully_invested == 1)
            .order_by("time_diff")
        )

        close_projects = await session.execute(stmt)

        close_projects = close_projects.all()

        projects = [
            {"name": name, "description": description, "time_diff": time_diff}
            for name, description, time_diff in close_projects
        ]

        # Время в секундах переводим в формат (дни, часы, минуты, секунды)
        for project in projects:
            td = timedelta(seconds=project["time_diff"])
            fmt = (
                f"{td.days}d "
                f"{td.seconds // SECONDS_IN_HOUR}h "
                f"{(td.seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE}m "
                f"{td.seconds % SECONDS_IN_MINUTE}s"
            )
            project["time_diff"] = fmt

        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
