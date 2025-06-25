from sqlalchemy import CheckConstraint, Column, String, Text

from .abstract_model import AbstractModel

MAX_LENGTH_FOR_NAME = 100


class CharityProject(AbstractModel):
    name = Column(
        String(MAX_LENGTH_FOR_NAME),
        CheckConstraint("LENGTH(name) >= 1"),
        unique=True,
        nullable=False,
    )
    description = Column(Text, nullable=False)
