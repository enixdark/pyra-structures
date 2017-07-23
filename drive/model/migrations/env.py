from __future__ import with_statement
from alembic import context
from sqlalchemy import create_engine, pool
import logging.config
import os.path

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if hasattr(config, 'config_file_name'):
    path = config.config_file_name
    here = os.path.abspath(os.path.dirname(path))
    logging.config.fileConfig(path, defaults={'here': here})

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import drive.model.meta.base
target_metadata = drive.model.meta.base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_section('db')['url']
    engine = create_engine(url, poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        transaction_per_migration=True,
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    raise NotImplementedError
else:
    run_migrations_online()
