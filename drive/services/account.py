import sqlalchemy as sa

from drive import model
from ..model.users import ROLES
log = __import__('logging').getLogger(__name__)

class AccountService:
    def __init__(self, db):
        self.db = db

    def create_user(self, first_name, last_name, email):
        """ Create a new user."""
        user = model.User()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = ROLES.NORMAL
        self.db.add(user)
        self.db.flush()
        log.info('created new user=%s with email=%s', user.id, email)
        return user

    def update_password(self, user, new_password):
        """ Update new password """
        account = (self.db.query(model.Account).filter(
            model.Account.user_id == user.id
        )).first()
        account.set_password(new_password)
        log.info('updated password user=%s', user.id)
        return account

    def update_profile(self, id, first_name, last_name, email, role = ROLES.NORMAL):
        """ Update profile """
        user = (self.db.query(model.User).filter(
            model.User.id == id
        )).first()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = role
        log.info('updated profile user=%s', user.id)
        return user

    def attach_account(self, user, password):
        """ Create a new local account with a password."""
        account = model.Account()
        account.user = user
        account.set_password(password)
        self.db.add(account)
        self.db.flush()
        log.info('created local account=%s for user=%s', account.id, user.id)
        return account

    def find_user_by_email(self, email):
        """ Find a user by email address."""
        user = (
            self.db.query(model.User)
            .filter(
                sa.func.lower(model.User.email) == sa.func.lower(email),
                model.User.is_deleted == sa.false(),
            )
        ).first()
        return user

    def find_user_by_id(self, id):
        """ Find a user by external identifier."""
        user = (
            self.db.query(model.User)
            .filter(
                model.User.id == id,
                model.User.is_deleted == sa.false(),
            )
        ).first()
        return user