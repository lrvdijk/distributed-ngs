import logging
import datetime
from math import ceil
from sqlalchemy import func
from json import dumps


from digs.common.actions import (HeartBeat, LocateData, JobRequest, GetAllDataLocs, RequestChunks, StoreData)
from digs.manager.db import Session
from digs.manager.models import DataLoc, DataNode, Data, UploadJob
from digs.messaging.protocol import DigsProtocolParser
from digs.exc import NotEnoughSpaceError

logger = logging.getLogger(__name__)

transient_parser = DigsProtocolParser()
persistent_parser = DigsProtocolParser()

transient_parser.define_action(HeartBeat)
transient_parser.define_action(LocateData)
transient_parser.define_action(GetAllDataLocs)
transient_parser.define_action(RequestChunks)
transient_parser.define_action(StoreData)

persistent_parser.define_action(JobRequest)


@transient_parser.register_handler(StoreData)
async def store_data(protocol, action):
    """This function handles a request from a client to locate a dataset."""
    session = Session()
    logger.debug("store_data call: %r, %r", protocol, action)

    if session.query(Data).filter_by(hash=action['hash']).first() is not None:
        # TODO send error message back
        result = {'err': "hash already in database!"}
        result_str = 'locate_data_result ' + dumps(result)
        await protocol.send_action(result_str)
        return

    con_job = session.query(UploadJob).filter_by(hash=action['hash']).first()

    if con_job is not None:  # The hash already exists in job list, continue work
        logger.debug("Hash found in jobs returning previous data node.")
        loc = session.query(DataNode).filter_by(id=con_job.data_node_id).first()
    else:  # New task found, get random DataNode
        logger.debug("New job, getting random DataNode.")
        loc = session.query(DataNode).filter(DataNode.free_space > action['size']).order_by(func.random()).first()
        if loc is None:
            logger.debug("loc is None")
            raise NotEnoughSpaceError(
                "Currently no nodes found with %s free space.", action['size']
            )
            return
        # TODO add and start using file path
        logger.debug("at TODO")

        new_job = UploadJob(data_node_id=loc.id,
                            size=action['size'],
                            type=action['type'],
                            upload_date=datetime.now(),
                            hash=action['hash'],
                            )

        logger.debug("after newjb TODO")
        loc.free_space = loc.free_space - action['size']
        session.add_all(new_job)
        session.commit()

    result = {'ip': loc.ip, 'socket': loc.socket}
    result_str = 'locate_data_result ' + dumps(result)
    await protocol.send_action(result_str)


@transient_parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to locate a dataset."""
    session = Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    data = session.query(DataLoc).filter_by(data_id=action['file_id']).order_by(func.random()).first()
    loc = session.query(DataNode).filter_by(id=data.data_node_id).first()
    result = {'ip': loc.ip, 'socket': loc.socket, 'path': data.file_path}
    result_str = 'locate_data_result ' + dumps(result)
    print(result_str)


@transient_parser.register_handler(GetAllDataLocs)
async def get_all_data_locs(protocol, action):
    """This function handles a request from a client to get_all_data_locations of a dataset."""
    session = Session()
    logger.debug("GetAllDataLocs call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    results = []
    for row in session.query(DataLoc).filter_by(data_id=action['file_id']).all():
        loc = session.query(DataNode).filter_by(id=row.data_node_id).first()
        results.append({'ip': loc.ip, 'socket': loc.socket, 'path': row.file_path})

    result_str = 'locate_data_results ' + dumps(results)
    print(protocol)
    protocol.send_action(result_str)


@transient_parser.register_handler(RequestChunks)
async def request_data_chunks(protocol, action):
    """This function handles a request from a client to a list of chunk requests of a dataset.
    """
    session = Session()
    logger.debug("Get chunks call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['end'])
    file_id = int(action['file_id'])
    start = int(action['start'])
    end = int(action['end'])
    chunk_size = int(action['chunk_size'])

    #TODO validate data parameters?

    tot_size = end - start
    num_chunks = ceil(tot_size / chunk_size)

    num_data_locs = session.query(DataLoc).filter_by(data_id=file_id).count()
    chunk_per_loc = num_chunks // num_data_locs
    chunks_left = num_chunks % num_data_locs

    chunk_requests = []
    chunk_start = start
    for idx, row in enumerate(session.query(DataLoc).filter_by(data_id=action['file_id']).all()):
        loc = session.query(DataNode).filter_by(id=row.data_node_id).first()
        node = {'ip': loc.ip, 'socket': loc.socket, 'path': row.file_path, 'chunks': []}
        for j in range(0, chunk_per_loc):
            node['chunks'].append({'chunk_start': chunk_start, 'chunk_end': min(chunk_start+chunk_size, end)})
            chunk_start += chunk_size
        if idx < chunks_left:  # Add leftover chunks spread over first nodes
            node['chunks'].append({'chunk_start': chunk_start, 'chunk_end': min(chunk_start + chunk_size, end)})
            chunk_start += chunk_size

        chunk_requests.append(node)

    logger.debug(chunk_requests)


@persistent_parser.register_handler(JobRequest)
async def job_request(protocol, action):
    """This function splits a job in to multiple sub jobs and puts them in
    the worker queue."""

    logger.debug("Job request: %r", action)
