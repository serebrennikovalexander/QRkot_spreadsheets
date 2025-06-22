from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class DonationBase(BaseModel):
    full_amount: Optional[PositiveInt]
    comment: Optional[str]


class DonationCreate(DonationBase):
    full_amount: PositiveInt


class DonationSmallDB(DonationCreate):
    comment: Optional[str]
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationFullDB(DonationSmallDB):
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
    user_id: Optional[int]
