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

    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

        while True:
            try:
                data = await self._stream_reader.readline()
                if self._stream_reader.at_eof():
                    continue

                logger.debug("process(): data %s", data)
                action, handlers = parser.parse(data)

                for handler in handlers:
                    self._loop.create_task(handler(self, action))
            except Exception as e:
                logger.exception("Error while handling data from the client")
                await self.error_handler(e)
