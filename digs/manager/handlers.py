import asyncio
import logging
import datetime

from pprint import pprint
from math import ceil
from json import dumps, loads

from sqlalchemy import func, and_

from digs.common.actions import (RegisterDataNode)
from digs.manager.models import DataLoc, DataNode, Data, UploadJob, Status
from digs.common.actions import (LocateData, JobRequest, GetAllDataLocs,
                                 RequestChunks, StoreData, StoreDataDone,
                                 FindOffsetsFASTA, ChunkOffsets, PerformMAFFT)
from digs.manager.db import Session
from digs.manager.models import DataLoc, DataNode, Data, UploadJob
from digs.messaging import persistent
from digs.messaging.protocol import DigsProtocolParser
from digs.exc import NotEnoughSpaceError, UnknownHash

logger = logging.getLogger(__name__)

transient_parser = DigsProtocolParser()
persistent_parser = DigsProtocolParser()


@transient_parser.register_handler(RegisterDataNode)
async def register_data_node(protocol, action):
    """This function registers a new data node at the manager."""
    session = Session()
    logger.debug("register_data_node call: %r, %r", protocol, action)

    data_node = session.query(DataNode).filter_by(ip=action['ip']).first()
    if data_node is None:
        datanode = DataNode(title="dataNode",
                            ip=action['ip'],
                            socket=action['socket'],
                            free_space=action['free_space'],
                            disk_space=action['disk_space'],
                            root_path=action['root_path'],
                            status=Status.ACTIVE,
                            )
        session.add(datanode)
        session.commit()
        results = {'succes': 'yes'}
        result_str = 'register_data_node_succes {}\n'.format(dumps(results))
    else:
        data_node.status = Status.ACTIVE
        session.commit()
        results = {'succes': 'Set status back on active'}
        result_str = 'register_data_node_succes {}\n'.format(dumps(results))

    await protocol.send_action(result_str)


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
    result_str = 'locate_data_result {}\n'.format(dumps(result))
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
        raise IOError("Cannot search for files using {}".format(
            action['search_by']
        ))

    data = session.query(DataLoc).filter_by(data_id=file_id).order_by(
        func.random()).first()

    logger.debug("Found data in DB: %s", data)

    if data is None:
        raise IOError("File with ID {} not found".format(file_id))

    loc = session.query(DataNode).filter(and_(DataNode.id == data.data_node_id, DataNode.status == Status.ACTIVE)) \
        .first()

    logger.debug("Location: %s", loc)
    result = {'ip': loc.ip, 'socket': loc.socket,
              'path': loc.root_path + '/' + data.file_path}
    result_str = 'locate_data_result {}\n'.format(dumps(result))
    await protocol.send_action(result_str)

    logger.debug("Sent locate_data result: %s", result_str)


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

    result_str = 'locate_data_results {}\n'.format(dumps(results))
    print(protocol)
    await protocol.send_action(result_str)


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
        loc = session.query(DataNode).filter(and_(DataNode.id == row.data_node_id, DataNode.status == Status.ACTIVE)) \
            .first()
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
    result_str = 'request_data_chunks_results {}\n'.format(dumps(
        chunk_requests))
    await protocol.send_action(result_str)


@persistent_parser.register_handler(JobRequest)
async def job_request(protocol, action):
    """This function splits a job in to multiple sub jobs and puts them in
    the worker queue."""

    # TODO: Currently only MAFFT supported
    assert action['job']['program_name'] == 'mafft'

    # First, ask a data node what proper splitting offsets are
    session = Session()

    file_id = action['job']['sequences']
    data_file = session.query(Data).filter_by(id=file_id).first()

    if data_file is None:
        raise Exception("File with ID {} does not exists!".format(file_id))

    reader = None
    writer = None
    data_loc = None
    data_node = None
    data_locs = session.query(DataLoc).filter(DataLoc.data_id == data_file.id).order_by(func.random()).all()
    for assoc in data_locs:
        data_node = session.query(DataNode).filter(and_(DataNode.id == assoc.data_node_id,
                                                        DataNode.status == Status.ACTIVE)).first()
        try:
            # Try available data nodes until someone responds
            reader, writer = await asyncio.open_connection(data_node.ip,
                                                           5001)
            data_loc = assoc
            break
        except OSError:
            reader = None
            writer = None

    if reader is None or writer is None:
        raise IOError("No available data node found for file id {}".format(
            file_id))

    file_path = data_node.root_path + "/" + data_loc.file_path
    action = 'find_offsets_fasta '
    data = {}
    data['file_path'] = file_path
    action = action + dumps(data) + '\n'
    # action = FindOffsetsFASTA(file_path=file_path)
    logger.debug("Sending action back: %s", str(action))
    writer.write(str(action).encode())
    await writer.drain()

    response = await reader.readline()
    parts = response.strip().split(maxsplit=1)
    logger.debug("Printing parts: %s",parts)
    resp = ChunkOffsets()
    assert parts[0].decode('utf-8') == resp.action
    resp.load_from_json(loads(parts[1].decode('utf-8')))
    writer.close()

    logger.debug("Got chunk offsets: %s", resp['offsets'])

    # For each chunk, create subtask in the queue for workers
    publisher = await persistent.create_publisher()
    publisher.channel.queue_declare('jobs.mafft', durable=True)
    for start, end in resp['offsets']:
        action = PerformMAFFT(
            sequences_data=file_id, chunk_start=start, chunk_end=end
        )

        # Publish to default exchange and jobs.mafft queue.
        await publisher.publish(str(action), "", "jobs.mafft")
