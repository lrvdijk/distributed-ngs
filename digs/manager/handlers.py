import logging
from sqlalchemy import func
from json import dumps

from digs.manager.actions import (parser, HeartBeat, LocateData, JobRequest, GetAllDataLocs)
from digs.manager.db import Session
from digs.manager.models import DataLoc, DataNode


logger = logging.getLogger(__name__)


@parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to locate a dataset."""
    session = Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    data = session.query(DataLoc).filter_by(data_id=file_id).order_by(func.random()).first()
    loc = session.query(DataNode).filter_by(id=data.data_node_id).first()
    result = {'ip': loc.ip, 'socket': loc.socket, 'path': data.file_path}
    result_str = 'locate_data_result ' + dumps(result)
    print(result_str)


@parser.register_handler(GetAllDataLocs)
async def get_all_data_locs(protocol, action):
    """This function handles a request from a client to get_all_data_locations of a dataset."""
    session = Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    results = []
    for row in session.query(DataLoc).filter_by(data_id=action['file_id']).all():
        loc = session.query(DataNode).filter_by(id=row.data_node_id).first()
        results.append({'ip': loc.ip, 'socket': loc.socket, 'path': row.file_path})

    result_str = 'locate_data_results ' + dumps(results)
    print(result_str)
