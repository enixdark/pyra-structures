from datetime import datetime
import sqlalchemy as sa

from sqlalchemy_utils.types import (
    PhoneNumber
)
from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Boolean,
    DateTime,
    Integer,
    Text,
    String,
    Boolean
)


from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)
from .meta.types import EmailAddress
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from .meta.base import fkey



class Driver(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'driver'

    id = Column(Integer, primary_key=True)
    
    user_id = fkey('user', nullable=False)
    user = relationship('User', back_populates='driver')
    drivers = relationship("DriverPolicy", back_populates="driver")
    policies = relationship("DriverPolicy", back_populates="policy")
    is_authorized = Column(Boolean, nullable=False)
    cdl_state = Column(Text, nullable=True)
    office_address = Column(Text, nullable=True)
    _office_phone_number = sa.Column(sa.Unicode(20))

    office_phone_number = sa.orm.composite(
        PhoneNumber,
        _office_phone_number,
    )
    license_number =  Column(Text, nullable=True)
    usdot = Column(Text, nullable = True)
    carrier_name = Column(Text, nullable = True)
    estimation = relationship('Estimation', back_populates='driver')
    group_id =  fkey('drivers', nullable=False)
    __repr_keys__ = ('id', 'user_id')

