import re

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData, Column, ForeignKey
from sqlalchemy.types import BigInteger

class _Base(object):
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])',
                   lambda m: '_' + m.group(0).lower(), name[1:])
        )

    # XXX SQLAlchemy has some shady warning if this is a 1-element tuple
    # where the item is a Column object. Thus we support using a 2-element
    # tuple with the second element being None.
    __repr_keys__ = ()

    id = Column(BigInteger, primary_key=True)

    def __repr__(self):
        kvpairs = (
            _repr_kvpair(self, k)
            for k in self.__repr_keys__ if k is not None
        )
        s = self.__class__.__name__
        s += '('
        s += ', '.join('%s=%r' % (k, v) for k, v in kvpairs)
        s += ')'
        return s

def _repr_kvpair(self, key):
    if isinstance(key, Column):
        key = key.name
    return key, getattr(self, key)

def fkey(table, **kw):
    return Column(
        BigInteger,
        ForeignKey(table + '.id', ondelete='cascade', onupdate='cascade'),
        **kw)

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

Base = declarative_base(cls=_Base, metadata=metadata)
