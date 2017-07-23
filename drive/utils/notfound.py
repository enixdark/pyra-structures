from pyramid.httpexceptions import (
    default_exceptionresponse_view,
    HTTPFound,
)
from pyramid.interfaces import IRoutesMapper

class RemoveSlashNotFoundViewFactory(object):
    def __init__(self, notfound_view=None):
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        path = request.path_info
        if path.endswith('/') and request.method in ('GET', 'OPTIONS', 'HEAD'):
            registry = request.registry
            mapper = registry.queryUtility(IRoutesMapper)
            if mapper is not None:
                newpath = path.rstrip('/')
                for route in mapper.get_routes():
                    if route.match(newpath) is not None:
                        qs = request.query_string
                        if qs:
                            qs = '?' + qs
                        return HTTPFound(location=newpath + qs)
        return self.notfound_view(context, request)
