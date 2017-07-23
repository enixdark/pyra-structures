from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import (
    DateTime,
    Boolean,
    Text,
)

from drive.utils.security import check_password, hash_password

class PasswordMixin(object):
    password_hash = Column('password', Text, nullable=True)
    password_changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password, pre_hashed=False):
        if not pre_hashed:
            password = hash_password(password)
        self.password_hash = password
        self.password_changed_at = datetime.utcnow().replace(microsecond=0)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password(password, self.password_hash)

class Creatable(object):
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Updatable(object):
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Activatable(object):
    _activated_at = Column('activated_at', DateTime, nullable=False, default=datetime.min)

    def _get_activated_at(self):
        if self._activated_at == datetime.min:
            return None
        return self._activated_at

    def _set_activated_at(self, value):
        if value is None:
            self._activated_at = datetime.min
        else:
            self._activated_at = value

    activated_at = hybrid_property(_get_activated_at, _set_activated_at)

    def _get_is_activated(self):
        return self._activated_at != datetime.min

    def _set_is_activated(self, value):
        if value != self._get_is_activated():
            self._activated_at = datetime.utcnow() if value else datetime.min

    is_activated = hybrid_property(_get_is_activated, _set_is_activated)



class Deletable(object):
    _deleted_at = Column('deleted_at', DateTime, nullable=False, default=datetime.min)

    def _get_deleted_at(self):
        if self._deleted_at == datetime.min:
            return None
        return self._deleted_at

    def _set_deleted_at(self, value):
        if value is None:
            self._deleted_at = datetime.min
        else:
            self._deleted_at = value

    deleted_at = hybrid_property(_get_deleted_at, _set_deleted_at)

    def _get_is_deleted(self):
        return self._deleted_at != datetime.min

    def _set_is_deleted(self, value):
        if value != self._get_is_deleted():
            self._deleted_at = datetime.utcnow() if value else datetime.min

    is_deleted = hybrid_property(_get_is_deleted, _set_is_deleted)
