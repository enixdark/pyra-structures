from sqlalchemy.types import TypeDecorator
from .security import hash_password
from sqlalchemy.types import Text

class EncryptPassword(TypeDecorator):
    """Allows storing and retrieving password hashes using PasswordHash."""
    impl = Text
    
    def __repr__(self):
        """Simple object representation."""
        return '<{}>'.format(type(self).__name__)

    @classmethod
    def new(cls, password, salt):
        """Creates a PasswordHash from the given password."""
        if isinstance(password, unicode):
            password = password.encode('utf8')
        return cls(hash_password(password, salt))