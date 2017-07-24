import sqlalchemy as sa
from sqlalchemy.orm import (
  backref,
  relation
)

from sqlalchemy.schema import Column
from sqlalchemy.types import (
    Text,
    DateTime,
)

from sqlalchemy_utils.types import (
    PhoneNumber
)

from .meta.base import Base
from .meta.base import fkey
from .meta.mixins import (
    Creatable,
    Updatable,
    Deletable,
    PasswordMixin,
)



class Account(Creatable, Updatable, Deletable, PasswordMixin, Base):
    __tablename__ = 'account'

    user_id = fkey('users', nullable=False, index=True, unique=True)
    user = relation('User', backref=backref('account', uselist=False))
    address = Column(Text, nullable = True)
    # _phone_number = sa.Column(sa.Unicode(20), nullable = True, default='000000000')
    phone_number = sa.Column(sa.Unicode(20), nullable = True, default='000000000')
    # phone_number = sa.orm.composite(
    #     PhoneNumber,
    #     _phone_number,
    # )
    last_login_at = Column(DateTime)

    __repr_keys__ = ('id', 'users_id')
