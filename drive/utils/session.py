import functools

log = __import__('logging').getLogger(__name__)

_marker = object()

SESSION_BINDING_TOKEN_KEY = '__ut'

def bind_session_to_user(request, user, session=None, invalidate=True):
    if session is None:
        old_val = getattr(request, '_skip_session_binding_checks', _marker)
        request._skip_session_binding_checks = True

        session = request.session

        if old_val is not _marker:
            request._skip_session_binding_checks = old_val
        else:
            del request._skip_session_binding_checks

    if invalidate:
        log.debug('invalidating session prior to bind')
        session.invalidate()

    token = make_session_token(request, user)
    log.info('binding session with token="%s"', token)
    session[SESSION_BINDING_TOKEN_KEY] = token

def make_session_token(request, user=_marker):
    uid = ''
    if user is _marker:
        user = request.user
    if user is not None:
        uid = 'u:{0}'.format(user.id)
    return uid

def session_protector(factory):
    @functools.wraps(factory)
    def wrapper(request):
        session = factory(request)

        if getattr(request, '_skip_session_binding_checks', False):
            log.debug('skipping automatic session binding')
            return session

        expected_token = make_session_token(request)
        found_token = session.get(SESSION_BINDING_TOKEN_KEY, '')
        invalid_session = False

        if expected_token:
            if found_token == expected_token:
                log.debug('found expected session binding token="%s"',
                          expected_token)

            elif found_token:
                log.info('detected session for token="%s" but '
                         'expected token="%s", invalidating session',
                         found_token, expected_token)
                invalid_session = True

            else:
                log.info('unbound session, expected token="%s", '
                         'invalidating session', expected_token)
                invalid_session = True

        elif found_token:
            log.info('detected bound session for token="%s" but '
                     'expected no token, invalidating session',
                     found_token)
            invalid_session = True

        else:
            log.debug('found unbound session')

        if invalid_session:
            session.invalidate()

            if expected_token:
                log.info('binding new session with token="%s"', expected_token)
                session[SESSION_BINDING_TOKEN_KEY] = expected_token

        return session
    return wrapper
