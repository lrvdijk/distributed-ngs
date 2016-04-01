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
class LocateData(Action):
    __action__ = 'locate_data'

    filenames = list

