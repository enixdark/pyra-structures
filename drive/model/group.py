from datetime import datetime
import sqlalchemy as sa


from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Text,
    Integer,
    Numeric,
)
from sqlalchemy_utils.types import (
    PhoneNumber
)

from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)
from sqlalchemy.orm import relationship


class Group(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    address = Column(Text, nullable=True)
    _phone_number = sa.Column(sa.Unicode(20))

    phone_number = sa.orm.composite(
        PhoneNumber,
        _phone_number,
    )
    drivers = relationship("Driver")
    __repr_keys__ = ('id')