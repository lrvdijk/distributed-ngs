from digs.messaging.parser import DigsParser
import asyncio


class DataNodeServerProtocol(asyncio.StreamReaderProtocol):
    """This class represents the TCP server protocol for a data node.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """
    def __call__(self):
        return self

    def connection_made(self, transport):
        """This function will be called by the asyncio event loop when a new
        client connects.

        :param transport: The transport object for this connection
        :type transport: asyncio.BaseTransport
        """
        super().connection_made(transport)
        print("Connection Made")
        self._stream_writer = asyncio.StreamWriter(transport, self,
                                                   self._stream_reader,
                                                   self._loop)

        self._loop.create_task(self.process())

    async def process(self):
        """Proceed to parse the incoming data, and deserialize the incoming
        JSON."""

        print("Process")
        print(self._stream_reader.readline())

        data = await self._stream_reader.readline()
        action, payload, handlers = DigsParser.parse(DigsParser(), data)

        for handler in handlers:
            self._loop.create_task(handler(self, payload))
