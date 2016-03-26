"""
Database Management
===================

This module provides some helper functions to manage database connections
and sessions.
"""

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker


session_factory = sessionmaker()
session = scoped_session(session_factory)  # TODO: define session scope


def initialize_db(connection_string):
    """
    Connect to the database specified by the connection string

    :param connection_string: A string specifying the database details. The
    format of this string can be found in the SQLAlchemy documentation.
    :type connection_string: str
    """

    engine = create_engine(connection_string)
    session.configure(bind=engine)


def initialize_easy_db(connection_string):
    """
    Connect to database specified by connection string

    :param connection_string: database to connect to
    """
    engine = create_engine(connection_string, echo=True)
    metadata = MetaData()
    data_entries = Table('data_entries', metadata, Column('id', Integer, primary_key=True), Column('path', String),)
    metadata.create_all(engine)
    # ins = data_entries.insert().values(path='DataFiles/DataNodes/testFasta.data')
    # ins.compile().params

    connection = engine.connect()
    # connection.execute(ins)
    return connection
