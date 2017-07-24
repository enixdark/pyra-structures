from drive.model.meta.engine import get_engine
from drive.model.meta.session import get_session_factory
from drive.model.meta.session import get_tm_session
from pyramid_mailer import Mailer

from .account import AccountService
from .login import LoginService
from .mail import MailService


log = __import__('logging').getLogger(__name__)

def includeme(config):
    settings = config.get_settings()

    settings.setdefault('tm.manager_hook', 'pyramid_tm.explicit_manager')

    config.include('pyramid_services')
    config.include('pyramid_tm')
    config.include('pyramid_retry')

    engine = get_engine(settings)
    dbmaker = get_session_factory(engine)
    config.registry['dbmaker'] = dbmaker

    def db_factory(context, request):
        return get_tm_session(dbmaker, request.tm)
    config.register_service_factory(db_factory, name='db')

    def account_factory(context, request):
        db = request.find_service(name='db')
        svc = AccountService(db)
        return svc
    config.register_service_factory(account_factory, AccountService)

    mailer = Mailer.from_settings(settings)
    def mailer_factory(context, request):
        return mailer.bind(transaction_manager=request.tm)
    config.register_service_factory(mailer_factory, name='mailer')

    def mail_service_factory(context, request):
        mailer = request.find_service(name='mailer')
        svc = MailService(settings=settings, mailer=mailer)
        return svc
    config.register_service_factory(mail_service_factory, MailService)

    def login_factory(context, request):
        db = request.find_service(name='db')
        svc = LoginService(db)
        return svc
    config.register_service_factory(login_factory, LoginService)

