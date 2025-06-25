from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt, validator

from app.models.charity_project import MAX_LENGTH_FOR_NAME

MIN_LENGTH_FOR_NAME = 1


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=MAX_LENGTH_FOR_NAME
    )
    description: Optional[str] = Field(None, min_length=MIN_LENGTH_FOR_NAME)
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=1, max_length=MAX_LENGTH_FOR_NAME)
    description: str = Field(..., min_length=MIN_LENGTH_FOR_NAME)
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):

    @validator("name")
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Имя проекта не может быть пустым!")
        return value


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: Optional[int]
    fully_invested: Optional[bool]
    create_date: Optional[datetime]
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
