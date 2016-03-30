from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from digs.db import ModelBase

class DataNode(ModelBase):
    """Sqlalchemy deals model"""
    __tablename__ = "data_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    location = Column('location', String, nullable=True)
    free_space = Column('free_space', Integer, nullable=True)
    disk_space = Column('disk_space', Integer, nullable=True)


class ComputationNode(ModelBase):
    """Sqlalchemy deals model"""
    __tablename__ = "computation_node"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    ip = Column('ip', String, nullable=False)
    location = Column('location', String, nullable=True)
    memory = Column('memory', Integer, nullable=True)
    cpu_power = Column('cpu_power', Integer, nullable=True)
