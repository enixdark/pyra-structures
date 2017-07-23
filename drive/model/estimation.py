from datetime import datetime
import sqlalchemy as sa


from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Text,
    Integer,
    Numeric,
)


from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)
from sqlalchemy.orm import relationship


class Estimation(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'estimation'

    id = Column(Integer, primary_key=True)
    price = Column(Numeric, nullable=False)
    time = Column(Numeric, nullable=False)
    driver = relationship('Driver', back_populates='estimation')

    __repr_keys__ = ('id')