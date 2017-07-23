from alembic.config import Config
from alembic.command import stamp
from alembic.command import upgrade

from drive.model.meta.base import metadata
from drive.model.meta.engine import (
    get_engine,
    get_current_version,
)

log = __import__('logging').getLogger(__name__)

def main(cli, args):
    cfg = Config(args.config_file)
    engine = get_engine(cli.settings, check_version=False)
    version = get_current_version(engine)
    if version is None:
        log.debug('initializing the database')
        metadata.create_all(bind=engine)
        stamp(cfg, 'head')

    else:
        log.debug('executing migrations')
        upgrade(cfg, args.rev)

    version = get_current_version(engine)
    log.info('database is now at revision=%s', version)
