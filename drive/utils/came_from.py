from urllib.parse import urlsplit, urlunsplit

log = __import__('logging').getLogger(__name__)

def get_came_from(request,
                  tag,
                  preferred_url=None,
                  preferred_route=None,
                  preferred_route_kw=None,
                  default_url=None,
                  default_route='index',
                  default_route_kw=None,
                  search=True,
                  allow_loops=False,
                  ):
    """ Find a URL that can be used as the return endpoint after processing.

    The ``tag`` must match for the ``came_from`` to be used from the session.

    Order of processing:
        - ``request.session['came_from']``
        - ``request.POST['came_from']``
        - ``request.GET['came_from']``
        - ``preferred_url``
        - ``request.route_url(preferred_route)``
        - ``request.referrer``
        - ``default_url``
        - ``request.route_url(default_route)``

    If ``search`` is ``False`` then only the session is checked.

    If ``allow_loops`` is ``False`` then the current url can never be
    returned from the session, POST, GET or referrer.

    This will return ``None`` if no url can be found. To ensure a URL is
    always returned make sure to set either ``preferred_url``, or
    ``preferred_route`` or ``default_url`` or ``default_route``.

    """
    came_from = None

    came_from = request.session.get('came_from.{}'.format(tag), {})
    if came_from:
        return came_from

    if not search:
        return came_from

    if not came_from:
        came_from = request.params.get('came_from')
        if check_came_from(request, came_from, allow_loops=allow_loops):
            return came_from

    if not came_from and preferred_url:
        return preferred_url

    if not came_from and preferred_route is not None:
        if preferred_route_kw is None:
            preferred_route_kw = {}
        return request.route_url(preferred_route, **preferred_route_kw)

    if not came_from:
        came_from = request.referrer
        if check_came_from(request, came_from, allow_loops=allow_loops):
            return came_from

    if default_url is not None:
        return default_url

    if default_route is not None:
        if default_route_kw is None:
            default_route_kw = {}
        return request.route_url(default_route, **default_route_kw)

def reset_came_from(request, tag):
    """ After processing a came_from url, reset it.

    This removes the ``came_from`` url from the session if it was stored there.
    If ``came_from`` is not ``None`` then the session will not be cleared
    unless the url is the same.

    """
    try:
        del request.session['came_from.{}'.format(tag)]
    except KeyError:
        pass

def set_came_from(request, tag, came_from=None, **kw):
    """ Store the ``came_from`` url in the session.

    If ``came_from`` is ``None`` then it will be guessed using
    :func:`.get_came_from`.

    Any extra arguments will be passed to :func:`.get_came_from`.

    """
    if came_from is None:
        came_from = get_came_from(request, tag, **kw)
    if came_from is None:
        reset_came_from(request, tag)
    else:
        request.session['came_from.{}'.format(tag)] = came_from
    return came_from

def check_came_from(request, came_from, allow_loops=False):
    """
    Validate ``came_from`` against the current ``request``.

    Returns ``False`` if the url is not hosted on the same domain as the
    current request for fear of hijacking attempts.

    If ``allow_loops`` is ``False`` and the ``came_from`` points to the same
    resource as the current URL then this will return ``False``.

    Returns ``True`` for valid URLs.

    """
    if not came_from:
        return False

    try:
        parts = urlsplit(came_from)
    except:
        # not a valid url
        return False

    # validate that came_from is mounted on the same domain
    if any([
        parts.netloc != request.host,
        parts.scheme != request.scheme,
    ]):
        log.info('filtering invalid came_from option=%s, invalid host/scheme',
                 came_from)
        return False

    # ensure the url is not the same
    if not allow_loops:
        new_parts = (parts.scheme, parts.netloc, parts.path, '', '')
        if urlunsplit(new_parts) == request.path_url:
            log.info('filtering invalid came_from option=%s, same url', came_from)
            return False
    return True
