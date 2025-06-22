from sqlalchemy import Column, ForeignKey, Integer, Text

from .abstract_model import AbstractModel


class Donation(AbstractModel):
    comment = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))
