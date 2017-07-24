from datetime import datetime
import sqlalchemy as sa

from drive import model
from drive.utils.encoding import datetime_to_int
from drive.utils.email_address import validate_email_address

log = __import__('logging').getLogger(__name__)

class LoginService:
    def __init__(self, db):
        self.db = db

    def make_token_for_user(self, user):
        """ Create an authentication token."""
        created_at_ts = datetime_to_int(user.last_credential_change_at)
        return f'1:{user.id}:{created_at_ts}'

    def find_user_from_token(self, token):
        """ Find a user from an authentication token."""
        uid, ts = None, None
        try:
            parts = token.split(':')
            if parts[0] == '1':
                uid, ts = parts[1:3]
                uid = int(uid)
                ts = int(ts)
        except Exception:
            log.debug('failed to deserialize access token=%s',
                      token, exc_info=True)
        # import ipdb;ipdb.set_trace()
        user = self.db.query(model.User).get(uid)

        if user is None:
            log.info('failed to find account for token="%s"', token)
        elif user.is_deleted:
            log.info('attempted login for deleted user=%s', user.id)
        elif datetime_to_int(user.last_credential_change_at) != ts:
            log.info('detected stale access token for user=%s', user.id)
        else:
            log.info('detected user=%s for token="%s"', user.id, token)
            return user

    def find_user_from_credentials(self, login, password):
        """ Find a user from their account credentials."""
        if not validate_email_address(login, raises=False):
            log.debug('login="%s" is not an email address', login)
            return None

        account = self._find_account_by_email(login)
        if account is not None and account.check_password(password):
            log.info('detected valid credentials, login="%s"', login)
            account.last_login_at = datetime.utcnow()
            account.user.last_login_at = account.last_login_at
            return account.user

        log.info('invalid login attempt, login="%s"', login)

    def _find_account_by_email(self, email):
        account = (
            self.db.query(model.Account)
            .join(model.Account.user)
            .filter(
                sa.func.lower(model.User.email) == sa.func.lower(email),
                model.Account.is_deleted == sa.false(),
                model.User.is_deleted == sa.false(),
            )
        ).first()

        return account
