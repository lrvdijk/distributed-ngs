import logging

from digs.manager.handlers import transient_parser, persistent_parser
from digs.messaging.transient import TransientProtocol
from digs.messaging.persistent import PersistentProtocol

logger = logging.getLogger(__name__)


class ManagerTransientProtocol(TransientProtocol):
    """This class represents the TCP server protocol for a manager node. For
    each client connection a new instance of this class will be created.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    @property
    def parser(self):
        return transient_parser


class ManagerPersistentProtocol(PersistentProtocol):
    @property
    def parser(self):
        return persistent_parser
