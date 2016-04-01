import logging
from sqlalchemy import func
from json import dumps

from digs.manager.actions import (parser, HeartBeat, LocateData, JobRequest)
from digs.manager.db import Session
from digs.manager.models import DataLoc, DataNode


logger = logging.getLogger(__name__)


@parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to locate a new dataset."""
    session = Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    file_id = action['file_id']
    data = session.query(DataLoc).filter_by(data_id=file_id).order_by(func.random()).first()
    loc = session.query(DataNode).filter_by(id=data.data_node_id).first()
    logger.debug(loc.ip)
    result = {'ip': loc.ip, 'socket': loc.socket, 'path': data.file_path}
    result_str = 'locate_data ' + dumps(result)
