from digs.messaging.protocol import DigsProtocolParser
from digs.messaging.actions import Action
from digs.common.actions import HeartBeat

parser = DigsProtocolParser()

parser.define_action(HeartBeat)


@parser.define_action
class LocateData(Action):
    __action__ = 'locate_data'

    filenames = list


@parser.define_action
class JobRequest(Action):
    __action__ = 'job_request'

    program = str  # program name
    argument = str  # program command line arguments
    dataset = int  # dataset id
