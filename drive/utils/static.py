import posixpath
from pyramid.path import AssetResolver
from pyramid.request import Request
from pyramid.static import ManifestCacheBuster
import re

from .settings import asbool

log = __import__('logging').getLogger(__name__)

def includeme(config):
    settings = config.get_settings()

    static_pkg = settings.get('static_pkg')
    manifest_path = settings.get('static_manifest')
    reload_assets = asbool(settings.get('pyramid.reload_assets', False))

    resolver = AssetResolver(config.root_package)

    # attempt to guess the static package path
    if static_pkg is None:
        spec = resolver.resolve('static')
    else:
        spec = resolver.resolve(static_pkg)
    if not spec.isdir():
        raise Exception(
            'The static asset folder cannot be found - specify a valid '
            'value for the "static_pkg" setting.')
    static_pkg = spec.absspec()
    settings['static_pkg'] = static_pkg

    # attempt to guess the manifest path
    if manifest_path is None:
        manifest_spec = resolver.resolve(static_pkg + '/manifest.json')
        manifest_path = manifest_spec.absspec()
        log.debug('attempting to guess manifest path="%s"', manifest_path)
        if not manifest_spec.exists():
            if not reload_assets:
                log.debug('disabling static manifest for pkg=%s',
                          config.root_package.__name__)
                manifest_path = None
    # if the user specified a manifest_path
    else:
        manifest_spec = resolver.resolve(manifest_path)
        manifest_path = manifest_spec.absspec()
        if not manifest_spec.exists():
            if not reload_assets:
                raise Exception(
                    'invalid "static_manifest" - either '
                    'remove the setting or create a valid manifest or '
                    'set "reload_assets=true" if it will be created later')
    settings['static_manifest'] = manifest_path

    # do not create cache buster unless necessary
    if manifest_path is not None:
        if not manifest_spec.exists():
            log.warn('starting with invalid static manifest="%s"',
                     manifest_path)
        cb = ManifestCacheBuster(
            manifest_path,
            reload=reload_assets,
        )
        config.add_cache_buster(static_pkg, cb)

        settings['asset_info'] = cb

    static_path = settings.get('static_url', 'static')
    config.add_static_view(
        static_path,
        static_pkg,
        cache_max_age=3600,
        factory=static_root_factory,
    )

    config.add_request_method(static_url)
    config.add_subscriber(renderer_globals, 'pyramid.interfaces.IBeforeRender')

def static_root_factory(request):
    request.is_static_asset = True

def static_url(request, spec, **kw):
    settings = request.registry.settings
    static_pkg = settings['static_pkg']
    if ':' not in spec:
        spec = posixpath.join(static_pkg, spec)
    return Request.static_url(request, spec, **kw)

def renderer_globals(event):
    request = event['request']
    settings = request.registry.settings
    event['static_url'] = request.static_url

    asset_info = settings.get('asset_info')
    event['use_asset_manifest'] = asset_info and bool(asset_info.manifest)

_static_regex = re.compile(
    r'''
    (?P<root>/static/[a-zA-Z0-9._/-]+)
    -
    (?P<buster>[a-fA-F0-9]+)
    (?P<ext>\.[a-zA-Z0-9]+)
    $''',
    re.VERBOSE,
)

def RemoveCacheBustTokenNotFoundViewFactory(wrapped):
    def wrapper(context, request):
        m = _static_regex.match(request.path_info)
        if m is not None and request.method in ('GET', 'OPTIONS', 'HEAD'):
            path = m.group('root') + m.group('ext')
            subreq = request.blank(
                path,
                base_url=request.application_url,
            )
            try:
                response = request.invoke_subrequest(subreq, use_tweens=False)
                response.cache_expires = 10 * 365 * 24 * 3600
                return response
            except Exception:
                pass
        return wrapped(context, request)
    return wrapper
