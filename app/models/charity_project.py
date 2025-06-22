from sqlalchemy import CheckConstraint, Column, String, Text

from .abstract_model import AbstractModel


class CharityProject(AbstractModel):
    name = Column(
        String(100),
        CheckConstraint("LENGTH(name) >= 1"),
        unique=True,
        nullable=False
    )
    description = Column(Text, nullable=False)
