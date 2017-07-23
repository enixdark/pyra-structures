from webob.exc import HTTPMovedPermanently
from webob.dec import wsgify

@wsgify.middleware
def SSLOnlyMiddleware(request, app):
    # check that the incoming request was using https
    if (
        request.scheme != 'https'
        and request.headers.get('X-Forwarded-Proto', 'http') != 'https'
    ):
        # redirect the user back using https
        https_url = request.url.replace('http://', 'https://')
        resp = HTTPMovedPermanently(location=https_url)
        resp.cache_expires = 86400
        return resp

    # override the request scheme to tell the app that we are using https
    request.scheme = 'https'
    return app

def make_filter(app, global_conf, **filter_settings):
    return SSLOnlyMiddleware(app)
