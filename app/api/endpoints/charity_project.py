from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_exists,
                                check_charity_project_full_amount,
                                check_charity_project_fully_invested,
                                check_charity_project_invested_amount,
                                check_charity_project_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import create_charity_project_investing

router = APIRouter()


@router.post(
    "/",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_charity_project_name_duplicate(charity_project.name, session)

    return await create_charity_project_investing(
        charity_project, session
    )


@router.get(
    "/",
    response_model=list[CharityProjectDB],
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """Для любого пользователя."""
    return await charity_project_crud.get_multi(session=session)


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(
        charity_project_id=project_id, session=session
    )

    await check_charity_project_fully_invested(charity_project=charity_project)

    if obj_in.name is not None:
        await check_charity_project_name_duplicate(obj_in.name, session)

    if obj_in.full_amount is not None:
        await check_charity_project_full_amount(
            charity_project=charity_project, new_full_amount=obj_in.full_amount
        )

    return await charity_project_crud.update(
        db_obj=charity_project, obj_in=obj_in, session=session
    )


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
    project_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(
        charity_project_id=project_id, session=session
    )

    await check_charity_project_invested_amount(
        charity_project=charity_project
    )

    await check_charity_project_fully_invested(charity_project=charity_project)

    return await charity_project_crud.remove(
        db_obj=charity_project, session=session
    )
