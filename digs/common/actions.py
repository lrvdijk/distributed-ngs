from digs.messaging.actions import Action


class HeartBeat(Action):
    __action__ = 'heartbeat'

    time = int
