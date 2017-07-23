from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory

import sqlalchemy as sa
from sqlalchemy.orm import configure_mappers

import weakref

from .types import (
    json_serializer,
    json_deserializer,
)

log = __import__('logging').getLogger(__name__)

engine_cache = weakref.WeakValueDictionary()

def get_engine(
    settings,
    prefix='db.',
    check_version=True,
    pessimistic=True,
):
    engine = None
    prefix = prefix or ''

    # pull out options because not all of them can be passed to
    # the engine_from_config fn
    opts = {
        k: v
        for k, v in settings.items()
        if k.startswith(prefix)
    }

    opts.pop(prefix + 'here', None)

    # attempt to load the engine from the cache
    # import ipdb;ipdb.set_trace()
    engine_id = opts.pop(prefix + 'engine_id')
    if engine_id:
        engine = engine_cache.get(engine_id)
        if engine:
            log.debug('using cached engine for id=%s', engine_id)

    # if no engine was found in the cache, load one
    if not engine:
        engine = sa.engine_from_config(
            opts,
            prefix,
            isolation_level='READ COMMITTED',
            json_serializer=json_serializer,
            json_deserializer=json_deserializer,
        )

        # assert the engine is at the correct migration
        if check_version:
            current_version = get_current_version(engine)
            log.info('current migration: %s', current_version)
            latest_version = get_latest_version(engine)
            log.debug('latest migration: %s', latest_version)

            if current_version != latest_version:
                raise RuntimeError(
                    'database versions out of sync, %s != %s' % (
                        current_version, latest_version))

        # for some reason the mappers are not properly configured at this stage
        # and some model objects were missing relationships such as
        # AppInstall.project_site_links
        configure_mappers()

        # store engine in cache
        if engine_id:
            engine_cache[engine_id] = engine

    if pessimistic and not getattr(engine, 'is_pessimistic', False):
        engine.is_pessimistic = True
        sa.event.listen(engine, 'engine_connect', ping_connection)

    return engine

def get_current_version(engine):
    conn = engine.connect()
    try:
        ctx = MigrationContext.configure(conn)
        return ctx.get_current_revision()
    finally:
        conn.close()

def get_latest_version(engine):
    cfg = Config()
    cfg.set_main_option('script_location', 'drive.model:migrations')
    script = ScriptDirectory.from_config(cfg)
    return script.get_current_head()

# http://docs.sqlalchemy.org/en/latest/core/pooling.html#disconnect-handling-pessimistic
def ping_connection(connection, branch):
    if branch:
        # "branch" refers to a sub-connection of a connection,
        # we don't want to bother pinging on these.
        return

    # turn off "close with result".  This flag is only used with
    # "connectionless" execution, otherwise will be False in any case
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        # run a SELECT 1.   use a core select() so that
        # the SELECT of a scalar value without a table is
        # appropriately formatted for the backend
        connection.scalar(sa.select([1]))
    except sa.exc.DBAPIError as err:
        # catch SQLAlchemy's DBAPIError, which is a wrapper
        # for the DBAPI's exception.  It includes a .connection_invalidated
        # attribute which specifies if this connection is a "disconnect"
        # condition, which is based on inspection of the original exception
        # by the dialect in use.
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.  The disconnect detection
            # here also causes the whole connection pool to be invalidated
            # so that all stale connections are discarded.
            connection.scalar(sa.select([1]))
            log.info('successfully refreshed a stale database connection')
        else:
            raise
    finally:
        # restore "close with result"
        connection.should_close_with_result = save_should_close_with_result
