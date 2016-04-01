from digs.messaging.protocol import DigsProtocolParser
from digs.messaging.actions import Action
from digs.common.actions import HeartBeat, JobRequest

parser = DigsProtocolParser()

parser.define_action(HeartBeat)
parser.define_action(JobRequest)


@parser.define_action
class Announce(Action):
    __action__ = 'announce'

    hostname = str
    type = str


@parser.define_action
class GetAllDataLocs(Action):
    __action__ = 'get_all_data_locs'

    file_id = int # data id


@parser.define_action
class LocateData(Action):
    __action__ = 'locate_data'

    file_id = int  # data id


@parser.define_action
class RequestChunks(Action):
    __action__ = 'request_data_chunks'

    file_id = int  # data id
    start = int # starting value for chunks
    end = int # end value of chunks
    chunk_size = int # size of chunks

