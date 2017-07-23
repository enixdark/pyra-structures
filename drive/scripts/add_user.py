import transaction

from drive.model.meta.session import get_tm_session
from drive.services.account import AccountService

from .validation import (
    validate_bool,
    validate_email,
    validate_password,
    validate_text,
)

log = __import__('logging').getLogger(__name__)

def create_user(cli, db):
    svc = AccountService(db)

    email = cli.prompt('Email: ', validate_email)

    user = svc.find_user_by_email(email)
    if user is not None:
        cli.abort('user already exists')

    first_name = cli.prompt('First Name: ', validate_text(min=1))
    last_name = cli.prompt('Last Name: ', validate_text(min=1))
    is_admin = cli.prompt('Admin? [y/N] ', validate_bool, default='n')
    password = cli.prompt(
        'Password: ', validate_password,
        confirm='Confirm Password: ', secure=True)

    user = svc.create_user(first_name, last_name, email)
    svc.attach_local_account(user, password)
    user.is_admin = is_admin
    return user

def main(cli, args):
    tm = transaction.TransactionManager(explicit=True)
    with tm:
        db = get_tm_session(cli.dbmaker, transaction_manager=tm)
        create_user(cli, db)
