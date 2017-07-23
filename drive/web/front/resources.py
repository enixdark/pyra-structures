from pyramid.security import (
    Allow, Authenticated
)


class Root(object):
    __acl__ = [
        (Allow, Authenticated, 'auth'),
    ]

    def __init__(self, request):
        self.request = request


def root_factory(request):
    return Root(request)
