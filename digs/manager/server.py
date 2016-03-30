from digs.common.server import ServerProtocol
from digs.manager.handlers import parser


class ManagerServerProtocol(ServerProtocol):
    """This class represents the TCP server protocol for a manager node. For
    each client connection a new instance of this class will be created.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

        data = await self._stream_reader.readline()
        action, handlers = parser.parse(data)

        for handler in handlers:
            self._loop.create_task(handler(self, action))
