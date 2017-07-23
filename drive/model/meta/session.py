from sqlalchemy.orm import sessionmaker

import zope.sqlalchemy

log = __import__('logging').getLogger(__name__)

def get_session_factory(engine):
    maker = sessionmaker()
    maker.configure(bind=engine)
    return maker

def get_tm_session(session_factory, transaction_manager):
    session = session_factory()
    zope.sqlalchemy.register(session, transaction_manager=transaction_manager)
    return session
