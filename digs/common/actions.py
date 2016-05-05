from digs.messaging.serialization import Serializable
from digs.messaging.actions import Action


class HeartBeat(Action):
    __action__ = 'heartbeat'

    time = int


class Error(Action):
    __action__ = 'error'

    kind = str
    message = str


class Announce(Action):
    __action__ = 'announce'

    hostname = str
    type = str


class Job(Serializable):
    program_name = str
    sequences = int


class JobRequest(Action):
    __action__ = 'job_request'

    job = Job


class PerformMAFFT(Action):
    __action__ = 'perform_bwa_job'

    sequences_data = int
    chunk_start = int
    chunk_end = int


class GetAllDataLocs(Action):
    __action__ = 'get_all_data_locs'

    file_id = int  # data id


class LocateData(Action):
    __action__ = 'locate_data'

    search_by = str  # type of search
    term = str  # The value for this search


class RequestChunks(Action):
    __action__ = 'request_data_chunks'

    file_id = int  # data id
    start = int  # starting value for chunks
    end = int  # end value of chunks
    chunk_size = int  # size of chunks


class StoreData(Action):
    __action__ = 'store_data'

    hash = int  # hash of the data
    size = int  # size of the shotgun read file in bytes.
    type = str  # the type of data to store


class StoreDataDone(Action):
    __action__ = 'store_data_done'

    hash = int  # hash of the data


class RegisterDataNode(Action):
    __action__ = 'register_data_node'

    ip = str  # Ip of the node
    socket = int  # socket used for node
    free_space = int  # free space
    disk_space = int  # total disk space
    root_path = str  # location to store data


class GetDataChunk(Action):
    __action__ = 'get_data_chunk'

    file_path = str
    chunk_start = int
    chunk_end = int


class FindOffsetsFASTQ(Action):
    __action__ = 'find_offsets_fastq'

    file_path = str


class FindOffsetsFASTA(Action):
    __action__ = 'find_offsets_fasta'

    file_path = str


class ChunkOffsets(Action):
    __action__ = 'chunk_offsets'

    offsets = list
