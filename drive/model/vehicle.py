from datetime import datetime
import sqlalchemy as sa


from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Text,
    Integer,
)


from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)
from sqlalchemy.orm import relationship


class Vehicle(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'policy'

    id = Column(Integer, primary_key=True)
    license_plate_number = Column(Text, nullable=False)
    
    truck_number = Column(Integer, nullable=False)
    drive = relationship("Policy", uselist=False, back_populates="policy")

