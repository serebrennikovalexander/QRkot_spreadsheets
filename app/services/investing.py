from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud, donation_crud
from app.models import CharityProject, Donation, User
from app.schemas.charity_project import CharityProjectCreate
from app.schemas.donation import DonationCreate


async def create_charity_project_investing(
    charity_project: CharityProjectCreate,
    session: AsyncSession,
) -> CharityProject:
    """Функция инвестирования при создании проекта."""

    new_project_data = charity_project.dict()

    new_project_data["invested_amount"] = 0

    while (
        new_project_data["full_amount"] > new_project_data["invested_amount"]
    ):
        # Ищем открытое пожертвование
        donation = await donation_crud.get_open_donation(session=session)

        # Если открытое пожертвование существет то выполняем следующие действия
        if donation is not None:
            donation_amount_delta = (
                donation.full_amount - donation.invested_amount
            )

            project_amount_delta = (
                new_project_data["full_amount"] -
                new_project_data["invested_amount"]
            )
            # Рассматриваем три случая

            # Первый случай
            if donation_amount_delta > project_amount_delta:
                donation.invested_amount += project_amount_delta
                # Закрываем проект
                await charity_project_crud.close_object_use_dict_data(
                    obj_in=charity_project,
                    obj_dict=new_project_data,
                    session=session
                )
                break

            # Второй случай
            if donation_amount_delta == project_amount_delta:
                # Закрываем пожертвование
                await donation_crud.close_object_use_db_data(
                    db_obj=donation,
                    session=session
                )
                # Закрываем проект
                await charity_project_crud.close_object_use_dict_data(
                    obj_in=charity_project,
                    obj_dict=new_project_data,
                    session=session
                )
                break

            # Третий случай
            if donation_amount_delta < project_amount_delta:
                # Закрываем пожертвование
                await donation_crud.close_object_use_db_data(
                    db_obj=donation,
                    session=session
                )
                new_project_data["invested_amount"] += donation_amount_delta
        else:
            break

    db_project = CharityProject(**new_project_data)

    return await charity_project_crud.save_object(
        db_obj=db_project,
        session=session
    )


async def create_donation_investing(
    new_donation: DonationCreate,
    session: AsyncSession,
    user: Optional[User] = None,
) -> Donation:
    """Функция инвестирования при создании пожертвования."""

    new_donation_data = new_donation.dict()

    if user is not None:
        new_donation_data["user_id"] = user.id

    new_donation_data["invested_amount"] = 0

    while (
        new_donation_data["full_amount"] > new_donation_data["invested_amount"]
    ):
        # Ищем открытый проекты
        charity_project = await charity_project_crud.get_open_charity_project(
            session=session
        )

        # Если открытый проек существет то выполняем следующие действия
        if charity_project is not None:
            project_amount_delta = (
                charity_project.full_amount - charity_project.invested_amount
            )

            donation_amount_delta = (
                new_donation_data["full_amount"] -
                new_donation_data["invested_amount"]
            )

            # Рассматриваем три случая

            # Первый случай
            if project_amount_delta > donation_amount_delta:
                charity_project.invested_amount += donation_amount_delta
                # Закрываем пожертование
                await donation_crud.close_object_use_dict_data(
                    obj_in=new_donation,
                    obj_dict=new_donation_data,
                    session=session
                )
                break

            # Второй случай
            if project_amount_delta == donation_amount_delta:
                # Закрываем проект
                await charity_project_crud.close_object_use_db_data(
                    db_obj=charity_project,
                    session=session
                )
                # Закрываем пожертование
                await donation_crud.close_object_use_dict_data(
                    obj_in=new_donation,
                    obj_dict=new_donation_data,
                    session=session
                )
                break

            # Третий случай
            if project_amount_delta < donation_amount_delta:
                # Закрываем проект
                await charity_project_crud.close_object_use_db_data(
                    db_obj=charity_project,
                    session=session
                )
                new_donation_data["invested_amount"] += project_amount_delta

        else:
            break

    db_donation = Donation(**new_donation_data)

    return await donation_crud.save_object(
        db_obj=db_donation,
        session=session
    )
