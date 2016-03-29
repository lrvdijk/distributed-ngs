import logging

from digs.manager.actions import (parser, HeartBeat, LocateData, JobRequest)

logger = logging.getLogger(__name__)


@parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to store a new dataset."""
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action values: %s", action.values)
