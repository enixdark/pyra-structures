from datetime import datetime
import sqlalchemy as sa


from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Boolean,
    DateTime,
    Integer,
    Text,
    String,
    Enum
)


from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)

from .meta.types import EmailAddress
from sqlalchemy.orm import (
    relationship, 
    validates
)



class ROLES(object):
    ADMIN = 'ADMIN'
    DRIVER = 'DRIVER'
    MANAGER = 'MANAGER'
    NORMAL = 'NORMAL'

    enum = Enum(
        ADMIN, DRIVER, MANAGER, NORMAL,
        metadata=Base.metadata,
        name='text'
    )

class User(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(EmailAddress, nullable=False)
    role = Column(ROLES.enum, nullable=True, default=ROLES.NORMAL)
    
    # driver = relationship('Driver', back_populates='user')
    

    last_credential_change_at = Column(
        DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint('email', 'deleted_at'),
    )
    __repr_keys__ = ('id', 'email')
