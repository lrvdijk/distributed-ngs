import os
import asyncio
import json
import logging
import uuid
import subprocess

from digs.common.utils import connect_to_random_central_server
from digs.common.actions import PerformMAFFT, LocateData, GetDataChunk
from digs.messaging.protocol import DigsProtocolParser
from digs.messaging.persistent import PersistentProtocol

persistent_parser = DigsProtocolParser()
logger = logging.getLogger(__name__)


class WorkerProtocol(PersistentProtocol):
    @property
    def parser(self):
        return persistent_parser


@persistent_parser.register_handler(PerformMAFFT)
async def perform_mafft(protocol, action):
    logger.debug("Accepting job: %s", action)
    # Retrieve chunk from data node
    # But first find the corresponding data nodes for the reads data and the
    # reference genome
    reader, writer = await connect_to_random_central_server()

    writer.write(str(
        LocateData(search_by='file_id', term=action['sequences_data'])
    ).encode())
    await writer.drain()

    data = await reader.readline()
    logger.debug("Received data: %s", data)
    parts = data.encode().strip().split(maxsplit=1)
    logger.debug("Parts received: %s", parts)

    assert parts[0] == 'locate_data_result'
    sequences_datanode = json.loads(parts[1])
    logger.info("Reads data node: %s", sequences_datanode)

    writer.close()

    # Create random job id, and create a new directory
    job_id = uuid.uuid4()
    path = os.path.join("jobs", str(job_id))
    os.makedirs(path, exist_ok=True)

    # Download reads data chunk
    reader, writer = await asyncio.open_connection(sequences_datanode['ip'],
                                                   5001)
    writer.write(str(
        GetDataChunk(
            file_path=sequences_datanode['path'],
            chunk_start=action['chunk_start'],
            chunk_end=action['chunk_end']
        )
    ).encode())

    size = action['chunk_end'] - action['chunk_start']
    read_bytes = 0

    with open(os.path.join(path, "sequences.fasta"), "wb") as f:
        while read_bytes < size:
            data = await reader.read(4096)
            read_bytes += len(data)

            if not data:
                raise IOError("Got EOF, but read only {} bytes of a chunk "
                              "with size {}".format(read_bytes, size))

            f.write(data)

    writer.close()

    with open(os.path.join(path, "msa_result.out"), "wb") as f:
        # Run MAFFT with quick tree generation method
        res = subprocess.run(["mafft", "--fastaparttree" "sequences.fasta"],
                             stdout=f, stderr=subprocess.PIPE)

        if res.returncode != 0:
            raise Exception(
                "MAFFT failed to run successfully: {}".format(res.stderr)
            )
