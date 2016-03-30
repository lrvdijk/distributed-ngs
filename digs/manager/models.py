import enum
from sqlalchemy import Enum, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

ModelBase = declarative_base()


class DataType:
    FASTA = 'fasta'
    RESULTS = 'results'
    TEXT = 'text'


class DataNode(ModelBase):
    """Sqlalchemy data node model"""
    __tablename__ = "data_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    socket = Column('socket', Integer, nullable=False)
    location = Column('location', String, nullable=True)
    free_space = Column('free_space', Integer, nullable=True)
    disk_space = Column('disk_space', Integer, nullable=True)


class ComputationNode(ModelBase):
    """Sqlalchemy computation node model"""
    __tablename__ = "computation_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    location = Column('location', String, nullable=True)
    memory = Column('memory', Integer, nullable=True)
    cpu_power = Column('cpu_power', Integer, nullable=True)

class Data(ModelBase):
    """Sqlalchemy data model"""
    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    size = Column('size', String, nullable=False)
    type = Column(Enum(DataType.FASTA, DataType.RESULTS, DataType.TEXT, name='data_type_enum'))
    upload_date = Column('upload_date', DateTime, nullable=False)


class DataLoc(ModelBase):
    """Sqlalchemy fasta data model"""
    __tablename__ = "data_loc"

    id = Column(Integer, primary_key=True)
    data_id = Column('data_id', Integer, ForeignKey('data.id'))
    data_node_id = Column('data_node_id', Integer, ForeignKey('data_node.id'))
    file_path = Column('file_path', String, nullable=False)
    UniqueConstraint('fasta_id', 'data_node_id')