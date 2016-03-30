from digs.messaging.protocol import DigsProtocolParser
from digs.messaging.actions import Action
from digs.common.actions import HeartBeat

parser = DigsProtocolParser()

parser.define_action(HeartBeat)


@parser.define_action
class GetDataChunk(Action):
    __action__ = 'get_data_chunk'

    file_path = str
    chunk_start = int
    chunk_end = int
