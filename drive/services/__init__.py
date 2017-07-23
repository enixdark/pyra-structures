from drive.model.meta.engine import get_engine
from drive.model.meta.session import get_session_factory
from drive.model.meta.session import get_tm_session
# from pyramid_mailer import Mailer

from .user import UserService

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


    def user_factory(context, request):
        db = request.find_service(name='db')
        svc = UserService(db)
        return svc
    config.register_service_factory(user_factory, UserService)