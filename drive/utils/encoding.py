import base64
from datetime import datetime, timedelta

EPOCH = datetime(1970, 1, 1)

def want_bytes(s, encoding='utf-8', errors='strict'):
    if isinstance(s, str):
        s = s.encode(encoding, errors)
    return s

def b64ws_encode(value):
    return base64.urlsafe_b64encode(value).strip(b'=').decode('ascii')

def b64ws_decode(value):
    value = want_bytes(value)
    return base64.urlsafe_b64decode(value + b'=' * (-len(value) % 4))

def datetime_to_int(value):
    return int((value - EPOCH).total_seconds())

def int_to_datetime(value):
    return EPOCH + timedelta(seconds=value)
