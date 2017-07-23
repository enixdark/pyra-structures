from pyramid.exceptions import BadCSRFToken
from pyramid.httpexceptions import (
    HTTPSeeOther,
)
from pyramid.view import forbidden_view_config
from pyramid.view import notfound_view_config
from pyramid.view import view_config

from drive.utils.came_from import check_came_from
from drive.utils.notfound import RemoveSlashNotFoundViewFactory
from drive.utils.static import RemoveCacheBustTokenNotFoundViewFactory

log = __import__('logging').getLogger(__name__)

@forbidden_view_config(
    renderer='404.jinja2',
)
def forbidden_view(exc, request):
    if request.authenticated_userid is not None:
        log.info('unauthorized access from user=%s',
                 request.authenticated_userid)
    else:
        log.info('unauthorized access from unknown user')

    request.response.status_code = 404
    return {}

@notfound_view_config(
    decorator=[
        RemoveSlashNotFoundViewFactory,
        RemoveCacheBustTokenNotFoundViewFactory,
    ],
    renderer='404.jinja2',
)
def not_found_view(exc, request):
    request.response.status_code = 404
    return {}

@view_config(
    context=BadCSRFToken,
)
def bad_csrf_view(exc, request):
    log.info('detected invalid csrf token')
    request.session.flash(
        'Invalid CSRF token. Make sure you have cookies enabled.',
        'error',
    )
    if check_came_from(request, request.referrer):
        next_url = request.referrer
    else:
        next_url = request.url
    return HTTPSeeOther(next_url)
