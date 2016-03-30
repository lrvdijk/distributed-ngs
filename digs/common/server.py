import logging
import asyncio
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class ServerProtocol(asyncio.StreamReaderProtocol, metaclass=ABCMeta):
    """This class represents the TCP server protocol for a manager node.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    def __init__(self, loop=None):
        stream_reader = asyncio.StreamReader(loop=loop)
        super().__init__(stream_reader, loop=loop)

    def connection_made(self, transport):
        """This function will be called by the asyncio event loop when a new
        client connects.

        :param transport: The transport object for this connection
        :type transport: asyncio.BaseTransport
        """
        super().connection_made(transport)
        logger.debug("Client connected: %s", transport.get_extra_info(
            'peername'))

        self._stream_writer = asyncio.StreamWriter(transport, self,
                                                   self._stream_reader,
                                                   self._loop)

        self._loop.create_task(self.process())

    def eof_received(self):
        # Close transport
        return False

    @abstractmethod
    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

