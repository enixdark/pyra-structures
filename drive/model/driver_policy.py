import sqlalchemy as sa
from .meta.base import Base

from sqlalchemy.orm import relationship
from .meta.base import fkey



class DriverPolicy(Base):
    __tablename__ = 'driver_policy'

    driver_id = fkey('driver', nullable=False)
    policy_id = fkey('policy', nullable=False)
    driver = relationship("Driver", back_populates="drivers")
    policy = relationship("Policy", back_populates="policies")
