from datetime import date, datetime
import json
from sqlalchemy import types
from sqlalchemy.dialects import postgresql as pg

from drive.utils import email_address

def _json_defaults(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, UUID):
        return str(value)
    elif hasattr(value, 'to_json'):
        return value.to_json()
    raise TypeError

def json_serializer(value):
    return json.dumps(value, default=_json_defaults)

def json_deserializer(value):
    return json.loads(value)

class JSON(types.TypeDecorator):
    impl = pg.JSONB()

class UUID(types.TypeDecorator):
    impl = pg.UUID(as_uuid=True)

class EmailAddress(types.TypeDecorator):
    impl = types.String(255)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = email_address.normalize(value, True)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = email_address.normalize(value, False)
        return value
