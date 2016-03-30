import logging

from digs.common.server import ServerProtocol
from digs.manager.handlers import parser

logger = logging.getLogger(__name__)


class ManagerServerProtocol(ServerProtocol):
    """This class represents the TCP server protocol for a manager node. For
    each client connection a new instance of this class will be created.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    @property
    def parser(self):
        return parser
