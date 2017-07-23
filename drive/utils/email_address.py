from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Validator
import re

class ValidateEmailAddress(Validator):
    """
    Copied from the Email Validator that comes with marshmallow
    but with the following changes:
     - Doesn't allow non-ascii characters in the user (mailbox) part
     - Doesn't allow literal IP addresses.
     - Does allow the domain part to be a bare TLD.
     - Doesn't try to validate the TLD differently.
     - Doesn't allow 'localhost'.
     - Doesn't allow addresses (post punycode expansion) > 254 characters
    """

    USER_REGEX = re.compile(
        r"(^[-!#$%&'*+/=?^`{}|~\w]+(\.[-!#$%&'*+/=?^`{}|~\w]+)*$"  # dot-atom
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]'
        r'|\\[\001-\011\013\014\016-\177])*"$)', re.IGNORECASE | re.UNICODE)

    DOMAIN_REGEX = re.compile(
        # domain
        r'^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*'
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.?)$',
        re.IGNORECASE | re.UNICODE)

    DOMAIN_BLACKLIST = ('localhost', 'localhost.')

    default_message = 'Not a valid email address.'

    def __init__(self, error=None):
        self.error = error or self.default_message

    def _format_error(self, value):
        return self.error.format(input=value)

    def __call__(self, value):
        message = self._format_error(value)

        if not value or '@' not in value:
            raise ValidationError(message)

        user_part, domain_part = value.rsplit('@', 1)

        try:
            user_part.encode('ascii')
        except UnicodeError:
            raise ValidationError(message + ' (non-ascii characters in mailbox part)')

        if not self.USER_REGEX.match(user_part):
            raise ValidationError(message +
                                  ' (unquoted special characters in mailbox part)')

        if domain_part.lower() in self.DOMAIN_BLACKLIST:
            raise ValidationError(message + ' (disallowed domain)')

        try:
            domain_part = domain_part.encode('idna').decode('ascii')
        except UnicodeError:
            raise ValidationError(message + ' (IDNA error)')

        if not self.DOMAIN_REGEX.match(domain_part):
            raise ValidationError(message + ' (invalid domain name)')

        # Per https://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
        if len(user_part) + 1 + len(domain_part) > 254:
            raise ValidationError(message + ' (too long)')

        return value


class EmailAddress(fields.ValidatedField, fields.String):
    """Copied from marshmallow.fields.Email but uses our custom validator"""

    default_error_messages = {'invalid': 'Not a valid email address.'}
    def __init__(self, *args, **kwargs):
        fields.String.__init__(self, *args, **kwargs)
        # Insert validation into self.validators so that multiple errors can be
        # stored.
        self.validators.insert(
            0,
            ValidateEmailAddress(error=self.error_messages['invalid'])
        )

    def _validated(self, value):
        if value is None:
            return None
        return ValidateEmailAddress(
            error=self.error_messages['invalid']
        )(value)


def validate_email_address(value, raises=True):
    validator = ValidateEmailAddress()
    try:
        validator(value)
    except ValidationError:
        if raises:
            raise
        return False
    return True


def normalize(email, wantpuny=True):
    # Technically, the mailbox part of the address is case-sensitive.
    # However, most server implementations treat the mailbox part as
    # not case-sensitive.
    #
    # To insure best compatibility, we do not fold the case of the mailbox
    # part as part of this normalization to preserve what was entered by
    # the user. However, queries against the database (e.g., to check for
    # duplicates) should be done in a case-insensitive way.
    #
    # For the domain part, we support IDNs by normalizing by encoding it to
    # 'idna'. The idna encoding takes care of RFC3490-specified details
    # which includes NFKC normalization. Also if there's a trailing
    # dot it is removed (unless the domain is a bare TLD in which case we
    # do append a dot).
    #
    # Note: email is assumed to have been validated at this point.

    (mailbox, domain) = email.rsplit('@', 1)

    fmt = 'ascii' if wantpuny else 'idna'
    domain = domain.encode('idna').decode(fmt).rstrip('.')
    if '.' not in domain:
        domain = domain + '.'

    return mailbox + '@' + domain
