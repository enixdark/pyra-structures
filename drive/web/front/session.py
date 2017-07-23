from pyramid.session import SignedCookieSessionFactory

from drive.utils.session import (
    bind_session_to_user,
    session_protector,
)
from drive.utils.settings import asbool

def includeme(config):
    settings = config.get_settings()

    session_factory = SignedCookieSessionFactory(
        settings['session.secret'],
        salt=settings['session.salt'],
        cookie_name=settings['session.cookie_name'],
        secure=asbool(settings['session.secure']),
        max_age=None,
        timeout=None,
        reissue_time=None,
        httponly=True,
        hashalg='sha256',
    )
    session_factory = session_protector(session_factory)
    config.set_session_factory(session_factory)
    config.add_request_method(bind_session_to_user)

    config.set_default_csrf_options(require_csrf=True)
