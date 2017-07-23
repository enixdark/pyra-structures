from datetime import timedelta
from configparser import ConfigParser
import os.path

from pyramid.config import Configurator
from pyramid.path import DottedNameResolver

from .resolver import caller_module

DEFAULT_BLACKLIST = (
    # stdlib logging
    'loggers'
    'logger_',
    'handlers',
    'handler_',
    'formatters',
    'formatter_',

    # pastedeploy
    'server:',
    'app:',
    'filter:',
    'composite:',
    'pipeline:',

    # alembic
    'alembic',
)

def load_settings_from_file(filename, blacklist=DEFAULT_BLACKLIST):
    here = os.path.abspath(os.path.dirname(filename))
    parser = ConfigParser({'here': here})
    parser.read(filename)

    settings = {}
    for section in parser.sections():
        if any(section.startswith(prefix) for prefix in blacklist):
            continue
        for k, v in parser.items(section):
            settings[section + '.' + k] = v

    return settings

def get_settings_with_prefix(settings, prefix):
    return {
        k[len(prefix):]: v
        for k, v in settings.items()
        if k.startswith(prefix)
    }

truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))

falsey = frozenset(('f', 'false', 'n', 'no', 'off', '0'))

def asbool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    value = str(value).strip()
    return value.lower() in truthy

def asduration(value, default=None):
    if value is None:
        return default

    if isinstance(value, int):
        return value

    value = int(value)
    return timedelta(seconds=value).total_seconds()

def aslist_cronly(value):
    return filter(None, [x.strip() for x in value.splitlines()])

def aslist(value, flatten=True):
    """
    Return a list of strings, separating the input based on newlines and,
    if ``flatten`` is ``True`` (the default), also split on spaces within
    each line.

    """
    values = aslist_cronly(value)
    if not flatten:
        return values
    return [sv for val in values for sv in val.split()]

def pyramid_config_from_settings(global_config, app_settings):
    config_file = global_config.get('__file__')
    settings = load_settings_from_file(config_file)
    settings.update(app_settings)

    caller = caller_module()
    resolver = DottedNameResolver(caller)
    package = resolver.get_package()
    config = Configurator(settings=settings, package=package)
    return config
