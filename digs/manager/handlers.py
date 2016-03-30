import logging

from digs.manager.actions import (parser, HeartBeat, LocateData, JobRequest)
from

logger = logging.getLogger(__name__)


@parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to locate a new dataset."""
    session = db.Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    file_id = action['file_id']
    for row in session.query(DataLoc).all():
        print(row.User, row.name)
