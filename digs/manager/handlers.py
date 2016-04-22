import asyncio
import logging
import datetime
from math import ceil
from json import dumps

from sqlalchemy import func

from digs.common.actions import (LocateData, JobRequest, GetAllDataLocs,
                                 RequestChunks, StoreData, StoreDataDone,
                                 FindOffsetsFASTQ, ChunkOffsets, PerformBWAJob)
from digs.manager.db import Session
from digs.manager.models import DataLoc, DataNode, Data, UploadJob
from digs.messaging import persistent
from digs.messaging.protocol import DigsProtocolParser
from digs.exc import NotEnoughSpaceError, UnknownHash

logger = logging.getLogger(__name__)

transient_parser = DigsProtocolParser()
persistent_parser = DigsProtocolParser()


@transient_parser.register_handler(StoreData)
async def store_data(protocol, action):
    """This function handles a request from a client to upload a dataset."""
    session = Session()
    logger.debug("store_data call: %r, %r", protocol, action)

    if session.query(Data).filter_by(hash=action['hash']).first() is not None:
        result = {'err': "hash already in database!"}
        result_str = 'store_data_err ' + dumps(result)
        await protocol.send_action(result_str)
        return

    con_job = session.query(UploadJob).filter_by(hash=action['hash']).first()

    # The hash already exists in job list, continue work
    if con_job is not None:
        logger.debug("Hash found in jobs returning previous data node.")
        loc = session.query(DataNode).filter_by(
            id=con_job.data_node_id).first()
    else:  # New task found, get random DataNode
        logger.debug("New job, getting random DataNode.")
        loc = session.query(DataNode).filter(
            DataNode.free_space > action['size']).order_by(
            func.random()).first()
        if loc is None:
            logger.debug("loc is None")
            raise NotEnoughSpaceError(
                "Currently no nodes found with %s free space.", action['size']
            )

        date = datetime.datetime.now()
        new_job = UploadJob(data_node_id=loc.id,
                            size=action['size'],
                            type=action['type'],
                            upload_date=date,
                            hash=action['hash'],
                            file_path=loc.root_path,
                            )
        loc.free_space = loc.free_space - action['size']
        session.add(new_job)
        session.commit()

    result = {'ip': loc.ip, 'socket': loc.socket, 'upload_path': loc.root_path}
    result_str = 'locate_data_result ' + dumps(result)
    await protocol.send_action(result_str)


@transient_parser.register_handler(StoreDataDone)
async def store_data_done(protocol, action):
    """This function handles a done message from a client about a upload."""
    session = Session()
    logger.debug("store_data_done call: %r, %r", protocol, action)

    con_job = session.query(UploadJob).filter_by(hash=action['hash']).first()
    if con_job is None:
        raise UnknownHash(
            "Currently hash found %s job not found.", action['hash']
        )
    loc = session.query(DataNode).filter_by(id=con_job.data_node_id).first()
    new_data = Data(size=con_job.size,
                    type=con_job.type,
                    upload_date=con_job.upload_date,
                    hash=con_job.hash,
                    )
    session.add(new_data)
    session.flush()
    session.refresh(new_data)

    new_data_loc = DataLoc(data_node_id=con_job.data_node_id,
                           data_id=new_data.id,
                           file_path=con_job.file_path,
                           )
    session.add(new_data_loc)
    session.delete(con_job)
    session.commit()


@transient_parser.register_handler(LocateData)
async def locate_data(protocol, action):
    """This function handles a request from a client to locate a dataset."""
    session = Session()
    logger.debug("locate_data call: %r, %r", protocol, action)
    logger.debug("Search by: %s", action['search_by'])
    if action['search_by'] == 'file_id':
        file_id = action['term']
    elif action['search_by'] == 'hash':
        file = session.query(Data).filter_by(hash=action['term']).first()
        if file is not None:
            file_id = file.id
    elif action['search_by'] == 'title':
        file = session.query(Data).filter_by(title=action['term']).first()
        if file is not None:
            file_id = file.id
    else:
        message = "Cannot search for files using: " + action['search_by']
        result = {'err': message}
        result_str = 'locate_data_err ' + dumps(result)
        await protocol.send_action(result_str)
        return

    data = session.query(DataLoc).filter_by(data_id=file_id).order_by(
        func.random()).first()
    if data is None:
        message = ("Could not locate file using: " + action['search_by'] +
                   " : " + action['term'])
        result = {'err': message}
        result_str = 'locate_data_err ' + dumps(result)
        await protocol.send_action(result_str)
        return
    loc = session.query(DataNode).filter_by(id=data.data_node_id).first()
    result = {'ip': loc.ip, 'socket': loc.socket, 'path': data.file_path}
    result_str = 'locate_data_result ' + dumps(result)
    await protocol.send_action(result_str)


@transient_parser.register_handler(GetAllDataLocs)
async def get_all_data_locs(protocol, action):
    """This function handles a request from a client to get_all_data_locations
    of a dataset."""

    session = Session()
    logger.debug("GetAllDataLocs call: %r, %r", protocol, action)
    logger.debug("action filenames: %s", action['file_id'])
    results = []
    for row in session.query(DataLoc).filter_by(
            data_id=action['file_id']).all():
        loc = session.query(DataNode).filter_by(id=row.data_node_id).first()
        results.append(
            {'ip': loc.ip, 'socket': loc.socket, 'path': row.file_path})

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

    # TODO validate data parameters?

    tot_size = end - start
    num_chunks = ceil(tot_size / chunk_size)

    num_data_locs = session.query(DataLoc).filter_by(data_id=file_id).count()
    chunk_per_loc = num_chunks // num_data_locs
    chunks_left = num_chunks % num_data_locs

    chunk_requests = []
    chunk_start = start
    for idx, row in enumerate(
            session.query(DataLoc).filter_by(data_id=action['file_id']).all()):
        loc = session.query(DataNode).filter_by(id=row.data_node_id).first()
        node = {'ip': loc.ip, 'socket': loc.socket, 'path': row.file_path,
                'chunks': []}
        for j in range(0, chunk_per_loc):
            node['chunks'].append({'chunk_start': chunk_start,
                                   'chunk_end': min(chunk_start + chunk_size,
                                                    end)})
            chunk_start += chunk_size
        if idx < chunks_left:  # Add leftover chunks spread over first nodes
            node['chunks'].append({'chunk_start': chunk_start,
                                   'chunk_end': min(chunk_start + chunk_size,
                                                    end)})
            chunk_start += chunk_size

        chunk_requests.append(node)

    logger.debug(chunk_requests)


@persistent_parser.register_handler(JobRequest)
async def job_request(protocol, action):
    """This function splits a job in to multiple sub jobs and puts them in
    the worker queue."""

    # TODO: Currently only BWA supported
    assert action['job']['program_name'] == 'bwa'

    # First, ask a data node what proper splitting offsets are
    session = Session()

    file_id = action['reads']
    data_file = session.query(Data).filter_by(id=file_id).first()

    if not data_file:
        raise IOError("File with id {} not found".format(file_id))

    reader, writer = None
    data_assoc = None
    for assoc in data_file.data_nodes.order_by(func.random()):
        try:
            # Try available data nodes until someone responds
            reader, writer = await asyncio.open_connection(assoc.data_node.ip,
                                                           5001)
            data_assoc = assoc
            break
        except OSError:
            reader, writer = None

    if reader is None and writer is None:
        raise IOError("No available data node found for file id {}".format(
            file_id))

    action = FindOffsetsFASTQ(file_path=data_assoc.file_path)
    writer.write(str(action).encode())
    await writer.drain()

    response = await reader.readline()
    parts = response.strip().split(maxsplit=1)

    resp = ChunkOffsets()
    assert parts[0] == resp.__action__
    resp.load_from_json(parts[1])
    writer.close()

    logger.debug("Got chunk offsets: %s", resp['offsets'])

    # For each chunk, create subtask in the queue for workers
    publisher = await persistent.create_publisher()
    for start, end in resp['offsets']:
        action = PerformBWAJob(
            reads_data=file_id, chunk_start=start, chunk_end=end,
            reference_genome=action['reference_genome']
        )

        # TODO: LEss hardcoded exchanges and routing keys
        await publisher.publish(str(action), "digs.messages", "jobs.bwa")
