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
    Enum
)


from .meta.base import Base
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
)
from .meta.types import EmailAddress
from sqlalchemy.orm import relationship
from ..utils.encrypt import EncryptPassword
from sqlalchemy.orm import validates




class ROLES(object):
    ADMIN = 'ADMIN'
    DRIVER = 'DRIVER'
    MANAGER = 'MANAGER'
    NORMAL = 'NORMAL'

    enum = Enum(
        ADMIN, DRIVER, MANAGER,
        metadata=Base.metadata,
        name='text'
    )

class User(Creatable, Updatable, Deletable, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(EmailAddress, nullable=False)
    role = Column(ROLES.enum, nullable=False, default=ROLES.NORMAL)
    address = Column(Text, nullable = True)
    password = Column(EncryptPassword)
    _phone_number = sa.Column(sa.Unicode(20))

    phone_number = sa.orm.composite(
        PhoneNumber,
        _phone_number,
    )
    driver = relationship('Driver', back_populates='user')


    # last_credential_change_at = Column(
    #     DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint('id', 'email'),
    )
    __repr_keys__ = ('id', 'email')

    @validates("password")
    def _validate_password(self, key, password):
        return getattr(type(self), key).type.validator(password)