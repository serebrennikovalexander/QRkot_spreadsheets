from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud, donation_crud
from app.models import CharityProject, Donation, User
from app.schemas.charity_project import CharityProjectCreate
from app.schemas.donation import DonationCreate


async def create_charity_project_investing(
    charity_project: CharityProjectCreate,
    session: AsyncSession
) -> CharityProject:
    """Основная функция инвестирования при создании проекта."""

    project_data = create_dict_with_charity_project_data(charity_project)
    await distribute_donations(project_data, charity_project, session)
    return await save_project(project_data, session)


async def distribute_donations(
    project_data: dict,
    charity_project: CharityProjectCreate,
    session: AsyncSession
) -> None:
    """Функция распределения пожертвований по проекту."""
    while needs_more_investment(project_data):
        # Ищем открытое пожертвование
        donation = await donation_crud.get_open_donation(session=session)
        if not donation:
            break
        # Если открытое пожертвование существует,
        # то выполняем процесс инвестирования
        await process_donation(
            donation, project_data, charity_project, session
        )
        if process_donation:
            break


async def process_donation(
    donation: Donation,
    project_data: dict,
    charity_project: CharityProjectCreate,
    session: AsyncSession
) -> None:
    """Обработка одного пожертвования."""
    donation_delta = calculate_delta_with_object(donation)
    project_delta = calculate_delta_with_dict(project_data)
    # Рассматриваем три случая
    # Первый случай
    if donation_delta > project_delta:
        donation.invested_amount += project_delta
        # Закрываем проект
        await close_project_use_dict_data(
            project_data,
            charity_project,
            session
        )
        return True  # Для выхода из внешено цикла while
    # Второй случай
    elif donation_delta == project_delta:
        # Закрываем пожертвование
        await close_donation_use_db_data(donation, session)
        # Закрываем проект
        await close_project_use_dict_data(
            project_data,
            charity_project,
            session
        )
        return True  # Для выхода из внешено цикла while
    # Третий случай
    else:
        # Закрываем пожертвование
        await close_donation_use_db_data(donation, session)
        project_data["invested_amount"] += donation_delta
    return False


async def create_donation_investing(
    donation: DonationCreate,
    session: AsyncSession,
    user: Optional[User] = None
) -> Donation:
    """Основная функция создания пожертвования с инвестированием."""

    donation_data = create_dict_with_donation_data(donation, user)
    await distribute_to_projects(donation_data, donation, session)
    return await save_donation(donation_data, session)


async def distribute_to_projects(
    donation_data: dict, donation: DonationCreate, session: AsyncSession
) -> None:
    """Распределение средств по проектам."""
    while needs_more_investment(donation_data):
        # Ищем открытый проект
        project = await charity_project_crud.get_open_charity_project(
            session=session
        )
        if not project:
            break
        # Если открытый проект существует,
        # то выполняем процесс инвестирования
        await process_project(project, donation_data, donation, session)
        if process_donation:
            break


async def process_project(
    project: CharityProject,
    donation_data: dict,
    donation: DonationCreate,
    session: AsyncSession
) -> None:
    """Обработка одного проекта."""
    project_delta = calculate_delta_with_object(project)
    donation_delta = calculate_delta_with_dict(donation_data)
    # Рассматриваем три случая
    # Первый случай
    if project_delta > donation_delta:
        project.invested_amount += donation_delta
        # Закрываем пожертвование
        await close_donation_use_dict_data(donation, donation_data, session)
        return True  # Для выхода из внешено цикла while
    # Второй случай
    elif project_delta == donation_delta:
        # Закрываем проект
        await close_project_use_db_data(project, session)
        # Закрываем пожертование
        await close_donation_use_dict_data(donation, donation_data, session)
        return True  # Для выхода из внешено цикла while
    # Третий случай
    else:
        # Закрываем проект
        await close_project_use_db_data(project, session)
        donation_data["invested_amount"] += project_delta
    return False


def create_dict_with_charity_project_data(
    charity_project: CharityProjectCreate
) -> dict:
    """
    Сохраняем данные из POST-запроса на создание
    проекта в словарь.
    """
    project_data = charity_project.dict()
    project_data["invested_amount"] = 0
    return project_data


def create_dict_with_donation_data(
    donation: DonationCreate,
    user: Optional[User] = None
) -> dict:
    """
    Сохраняем данные из POST-запроса на создание
    пожертвования в словарь.
    """
    donation_data = donation.dict()
    donation_data["invested_amount"] = 0
    if user:
        donation_data["user_id"] = user.id
    return donation_data


def needs_more_investment(data: dict) -> bool:
    """Проверка необходимости дополнительных инвестиций."""
    return data["full_amount"] > data["invested_amount"]


def calculate_delta_with_object(object: Donation | CharityProject) -> int:
    return object.full_amount - object.invested_amount


def calculate_delta_with_dict(data: dict) -> int:
    return data["full_amount"] - data["invested_amount"]


async def close_project_use_dict_data(
    project_data: dict,
    charity_project: CharityProjectCreate,
    session: AsyncSession
) -> None:
    """Закрытие проекта испоьзуя словарь."""
    await charity_project_crud.close_object_use_dict_data(
        obj_in=charity_project,
        obj_dict=project_data,
        session=session,
    )


async def close_project_use_db_data(
    project: CharityProject, session: AsyncSession
) -> None:
    """Закрытие проекта используя объект из БД."""
    await charity_project_crud.close_object_use_db_data(
        db_obj=project, session=session
    )


async def close_donation_use_dict_data(
    donation: DonationCreate, donation_data: dict, session: AsyncSession
) -> None:
    """Закрытие пожертвования используя словарь."""
    await donation_crud.close_object_use_dict_data(
        obj_in=donation,
        obj_dict=donation_data,
        session=session,
    )


async def close_donation_use_db_data(
        donation: Donation,
        session: AsyncSession
) -> None:
    """Закрытие пожертвования используя объект из БД."""
    await donation_crud.close_object_use_db_data(
        db_obj=donation, session=session
    )


async def save_project(
    project_data: dict, session: AsyncSession
) -> CharityProject:
    """Сохранение проекта в БД."""

    db_project = CharityProject(**project_data)
    return await charity_project_crud.save_object(
        db_obj=db_project, session=session
    )


async def save_donation(
    donation_data: dict, session: AsyncSession
) -> Donation:
    """Сохранение пожертвования в БД."""
    db_donation = Donation(**donation_data)
    return await donation_crud.save_object(db_obj=db_donation, session=session)
