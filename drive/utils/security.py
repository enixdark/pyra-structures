import bcrypt
import binascii
from datetime import datetime, timedelta
import hashlib
import hmac
import json

from .encoding import (
    b64ws_decode,
    b64ws_encode,
    datetime_to_int,
    int_to_datetime,
    want_bytes,
)

class SignatureExpired(Exception):
    def __init__(self, message, payload=None, date_signed=None):
        Exception.__init__(self, message)
        self.payload = payload
        self.date_signed = date_signed

def signed_serialize(secret, value, now=None):
    if now is None:
        now = datetime.utcnow()

    now_offset = datetime_to_int(now)
    appstruct = (value, now_offset)
    cstruct = want_bytes(json.dumps(appstruct, separators=(',', ':')))
    sig = hmac.new(want_bytes(secret), cstruct, hashlib.sha256).digest()
    return b64ws_encode(cstruct + sig)

def signed_deserialize(secret, value, max_age=None, now=None):
    try:
        fstruct = b64ws_decode(value)
    except (binascii.Error, TypeError) as e:
        raise ValueError('badly formed base64 data: %s' % e)
    cstruct = fstruct[:-32]
    expected_sig = fstruct[-32:]

    sig = hmac.new(want_bytes(secret), cstruct, hashlib.sha256).digest()
    if not constant_time_compare(sig, expected_sig):
        raise ValueError('invalid signature')

    content, creation_time_offset = json.loads(cstruct.decode('utf-8'))
    if max_age is not None:
        creation_time = int_to_datetime(creation_time_offset)
        if now is None:
            now = datetime.utcnow()
        age = now - creation_time

        if isinstance(max_age, (float, int)):
            max_age = timedelta(seconds=max_age)
        if age > max_age:
            raise SignatureExpired(
                'Signature age {} > {} seconds'.format(
                    age.total_seconds(), max_age.total_seconds(),
                ),
                content,
                creation_time)
    return content

def constant_time_compare(val1, val2):
    """Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.  Do
    not use this function for anything else than comparision with known
    length targets.

    """
    len_eq = len(val1) == len(val2)
    if len_eq:
        result = 0
        left = val1
    else:
        result = 1
        left = val2
    # even with compare_digest it's not clear whether it properly
    # compares strings of differing lengths using constant-time
    # so we still use ``left`` here.
    result += not hmac.compare_digest(left, val2)
    return result == 0

def hash_password(password, salt=None):
    """Create a hashed version of a given password."""
    if salt is None:
        salt = bcrypt.gensalt()
    raw_pw = want_bytes(password)
    return bcrypt.hashpw(raw_pw, salt).decode('utf8')

def check_password(password, hashed_password):
    """Verify that a password matches a given hashed password."""
    return bcrypt.checkpw(want_bytes(password), want_bytes(hashed_password))

def compute_stream_digest(fp, blocksize=65536, hash_fn=hashlib.sha512):
    hasher = hash_fn()
    block = fp.read(blocksize)
    while block:
        hasher.update(want_bytes(block))
        block = fp.read(blocksize)
    return hasher.hexdigest()
