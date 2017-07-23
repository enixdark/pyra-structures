from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.security import (
    Authenticated,
    Everyone,
)

from drive.utils.settings import asbool
from drive import services as S
from .resources import root_factory

class AuthenticationPolicy(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, request):
        if request.user:
            return request.user.id

    def effective_principals(self, request):
        principals = [Everyone]

        if request.user:
            principals += [Authenticated]

        return principals

def get_user(request):
    token = request.unauthenticated_userid
    if token:
        svc = request.find_service(S.LoginService)
        return svc.find_user_from_token(token)

_default_vary = set([
    'Cookie',
    'Accept',
    'Accept-Language',
    'Authorization',
])

_default_static_vary = set([
    'Accept',
    'Accept-Language',
])

def new_response_subscriber(event):
    request = event.request
    response = event.response

    if getattr(request, 'is_static_asset', False):
        vary = _default_static_vary
    else:
        vary = _default_vary

    if response.vary is not None:
        response.vary = vary.union(response.vary)
    else:
        response.vary = vary

def includeme(config):
    settings = config.get_settings()

    authn_policy = AuthenticationPolicy(
        settings['auth.secret'],
        cookie_name=settings['auth.cookie_name'],
        secure=asbool(settings['auth.secure']),
        max_age=None,
        timeout=None,
        reissue_time=None,
        hashalg='sha256',
    )
    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)

    config.set_root_factory(root_factory)

    config.add_subscriber(new_response_subscriber,
                          'pyramid.events.NewResponse')
