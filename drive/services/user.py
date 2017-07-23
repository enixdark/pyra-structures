import uuid
import sqlalchemy as sa
from drive import model

log = __import__('logging').getLogger(__name__)


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, first_name, last_name):
        """ Create a new user."""
        user = model.User()
        user.first_name = first_name
        user.last_name = last_name

        self.db.add(user)
        self.db.flush()
        log.info('created new user=%s', user.id)
        return user

    def find_user_by_id(self, id):
        """ Find an existing project by external identifier."""
       
        return self.db.query(model.User).filter(model.User.id == id)
        # .filter(
        #     model.User.slug == id,
        #     model.User.is_deleted == sa.false(),
        # ).first()
