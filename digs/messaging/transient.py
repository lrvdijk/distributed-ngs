import logging
import asyncio
from abc import abstractproperty

from digs.common.actions import Error
from digs.messaging.protocol import BaseProtocol

logger = logging.getLogger(__name__)


class TransientProtocol(asyncio.StreamReaderProtocol, BaseProtocol):
    """This class represents the TCP server protocol for any node.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    def __init__(self, loop=None):
        stream_reader = asyncio.StreamReader(loop=loop)
        super().__init__(stream_reader, loop=loop)

        self.data_processor = None

    @abstractproperty
    def parser(self):
        pass

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

        self.data_processor = self._loop.create_task(self.process())

    async def error_handler(self, exc):
        action = Error(kind=exc.__class__.__name__, message=str(exc))
        return await self.send_action(action)

    def eof_received(self):
        self.data_processor.cancel()
        # Close transport
        return False

    async def send_action(self, action):
        self._stream_writer.write(str(action).encode())
        return await self._stream_writer.drain()

    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

        # TODO: add some keep-alive mechanism to automatically close
        # connections idle for some time.
        while True:
            try:
                data = await self._stream_reader.readline()
                logger.debug("process(): data %s", data)

                if len(data.strip()) == 0:
                    continue

                action, handler = self.parser.parse(data)

                logger.debug("Scheduling handler %r", handler)
                self._loop.create_task(handler(self, action))
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.debug("Processing task cancelled.")
                break
            except Exception as e:
                logger.exception("Error while handling data from the client")
                await self.error_handler(e)
