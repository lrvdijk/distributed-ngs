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


class DataLoc(ModelBase):
    """Association table between data files and data nodes. A data file can
    be replicated across multiple nodes."""

    __table_args__ = {'extend_existing': True}
    __tablename__ = "data_loc"

    data_id = Column(Integer, ForeignKey('data.id'),
                     primary_key=True)
    data_node_id = Column(Integer, ForeignKey('data_node.id'),
                          primary_key=True)
    file_path = Column(String, nullable=False)

    dara_node = relationship("DataNode", back_populates="data_files")
    data_file = relationship("Data", back_populates="data_nodes")


class DataNode(ModelBase):
    """Sqlalchemy data node model"""
    __table_args__ = {'extend_existing': True}
    __tablename__ = "data_node"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    ip = Column(String, nullable=False)
    socket = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    root_path = Column(String, nullable=True)  # TODO should become false.
    free_space = Column(Integer, nullable=True)
    disk_space = Column(Integer, nullable=True)

    data_files = relationship("DataLoc", back_populates="data_node")


class Data(ModelBase):
    """Sqlalchemy data model"""

    __table_args__ = {'extend_existing': True}
    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    size = Column(String, nullable=False)
    type = Column(Enum(
        DataType.FASTA, DataType.RESULTS, DataType.TEXT, DataType.SHOTGUN,
        name='data_type_enum'
    ))
    hash = Column(Integer, nullable=False)
    upload_date = Column(DateTime, nullable=False)

    data_nodes = relationship("DataLoc", back_populates="data_file")


class ComputationNode(ModelBase):
    """Sqlalchemy computation node model"""
    __table_args__ = {'extend_existing': True}
    __tablename__ = "computation_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    location = Column('location', String, nullable=True)
    memory = Column('memory', Integer, nullable=True)
    cpu_power = Column('cpu_power', Integer, nullable=True)


class UploadJob(ModelBase):
    """Sqlalchemy fasta upload job model"""

    __table_args__ = {'extend_existing': True}
    __tablename__ = "upload_job"

    id = Column(Integer, primary_key=True)
    data_node_id = Column('data_node_id', Integer, ForeignKey('data_node.id'))
    file_path = Column('file_path', String)
    title = Column('title', String)
    size = Column('size', String, nullable=False)
    type = Column(Enum(
        DataType.FASTA, DataType.RESULTS, DataType.TEXT, DataType.SHOTGUN,
        name='data_type_enum'
    ))
    upload_date = Column('upload_date', DateTime, nullable=False)
    client_id = Column('client_id', Integer)
    client_name = Column('client_name', String)
    hash = Column('hash', Integer, nullable=False)

