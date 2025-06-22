from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class AbstractModel(Base):
    """Абстрактный класс для моделей проектов и пожертвований"""

    __abstract__ = True

    full_amount = Column(Integer, CheckConstraint("full_amount > 0"))
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, index=True, default=datetime.utcnow)
    close_date = Column(DateTime)
