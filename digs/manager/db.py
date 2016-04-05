"""
Database Management
===================

This module provides some helper functions to manage database connections
and sessions.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import URL

from digs.manager.models import ModelBase
from settings import DATABASE

logger = logging.getLogger(__name__)

engine = None
session_factory = sessionmaker()
Session = scoped_session(session_factory)  # TODO: define session scope


def initialize_db(connection_string):
    """
    Connect to the database specified by the connection string

    :param connection_string: A string specifying the database details. The
    format of this string can be found in the SQLAlchemy documentation.
    :type connection_string: str
    """

    global engine

    engine = create_engine(URL(**DATABASE))
    Session.configure(bind=engine)


def create_tables():
    """Create all corresponding database tables subclassing from `ModelBase`."""
    ModelBase.metadata.create_all(engine)
    logger.debug('create')
    logger.debug(engine)

