from digs.common.server import TransientProtocol
from digs.data_node.handlers import parser


class DataNodeTransientProtocol(TransientProtocol):
    """This class represents the TCP server protocol for a data node.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """

    @property
    def parser(self):
        return parser

    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

        data = await self._stream_reader.readline()
        action, handlers = parser.parse(data)

        for handler in handlers:
            self._loop.create_task(handler(self, action))
