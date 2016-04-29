import enum
from sqlalchemy import Enum, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

ModelBase = declarative_base()

# TODO remove extended existing


class DataType:
    FASTA = 'fasta'
    RESULTS = 'results'
    TEXT = 'text'
    SHOTGUN = 'shotgun'

class Status:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    UNKNOWN = 'unknown'


class DataNode(ModelBase):
    __table_args__ = {'extend_existing': True}
    """Sqlalchemy data node model"""
    __tablename__ = "data_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    socket = Column('socket', Integer, nullable=False)
    location = Column('location', String, nullable=True)
    root_path = Column('root_path', String, nullable=True)  # TODO should become false.
    free_space = Column('free_space', Integer, nullable=True)
    disk_space = Column('disk_space', Integer, nullable=True)
    status = Column(Enum(Status.ACTIVE, Status.INACTIVE, Status.UNKNOWN, name='status_enum'))


class ComputationNode(ModelBase):
    __table_args__ = {'extend_existing': True}
    """Sqlalchemy computation node model"""
    __tablename__ = "computation_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    location = Column('location', String, nullable=True)
    memory = Column('memory', Integer, nullable=True)
    cpu_power = Column('cpu_power', Integer, nullable=True)

class Data(ModelBase):
    __table_args__ = {'extend_existing': True}
    """Sqlalchemy data model"""
    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    size = Column('size', String, nullable=False)
    type = Column(Enum(DataType.FASTA, DataType.RESULTS, DataType.TEXT, DataType.SHOTGUN, name='data_type_enum'))
    hash = Column('hash', Integer, nullable=False)
    upload_date = Column('upload_date', DateTime, nullable=False)


class DataLoc(ModelBase):
    __table_args__ = {'extend_existing': True}
    """Sqlalchemy fasta data model"""
    __tablename__ = "data_loc"

    id = Column(Integer, primary_key=True)
    data_id = Column('data_id', Integer, ForeignKey('data.id'))
    data_node_id = Column('data_node_id', Integer, ForeignKey('data_node.id'))
    file_path = Column('file_path', String, nullable=False)
    UniqueConstraint('fasta_id', 'data_node_id')


class UploadJob(ModelBase):
    __table_args__ = {'extend_existing': True}
    """Sqlalchemy fasta upload job model"""
    __tablename__ = "upload_job"

    id = Column(Integer, primary_key=True)
    data_node_id = Column('data_node_id', Integer, ForeignKey('data_node.id'))
    file_path = Column('file_path', String)
    title = Column('title', String)
    size = Column('size', String, nullable=False)
    type = Column(Enum(DataType.FASTA, DataType.RESULTS, DataType.TEXT, DataType.SHOTGUN, name='data_type_enum'))
    upload_date = Column('upload_date', DateTime, nullable=False)
    client_id = Column('client_id', Integer)
    client_name = Column('client_name', String)
    hash = Column('hash', Integer, nullable=False)

