from digs.messaging.actions import Action


class HeartBeat(Action):
    __action__ = 'heartbeat'

    time = int


class Error(Action):
    __action__ = 'error'

    kind = str
    message = str
