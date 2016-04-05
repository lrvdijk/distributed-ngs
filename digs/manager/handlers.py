import logging

from digs.messaging.protocol import DigsProtocolParser
from digs.common.actions import LocateData, JobRequest

logger = logging.getLogger(__name__)

transient_parser = DigsProtocolParser()
persistent_parser = DigsProtocolParser()


@transient_parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to store a new dataset."""
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['filenames'])


@persistent_parser.register_handler(JobRequest)
async def job_request(protocol, action):
    """This function splits a job in to multiple sub jobs and puts them in
    the worker queue."""

    logger.debug("Job request: %r", action)
