"""
Database Management
===================

This module provides some helper functions to manage database connections
and sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


session_factory = sessionmaker()
Session = scoped_session(session_factory)  # TODO: define session scope


def initialize_db(connection_string):
    """
    Connect to the database specified by the connection string

    :param connection_string: A string specifying the database details. The
    format of this string can be found in the SQLAlchemy documentation.
    :type connection_string: str
    """

    engine = create_engine(connection_string)
    Session.configure(bind=engine)
