from digs.messaging.protocol import DigsProtocolParser
import asyncio
import logging


class DataNodeServerProtocol(asyncio.StreamReaderProtocol):
    """This class represents the TCP server protocol for a data node.

    It handles the receiving a sending of messages, and automatically
    deserializes incoming data.
    """
    def __init__(self, reader, node):
        self.node = node
        super(DataNodeServerProtocol, self).__init__(reader)

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
        action, payload, handlers = DigsProtocolParser.parse(DigsProtocolParser(), data)

        if action == 'chunk':
            logging.debug(action)
            response = self.node.get_chunk(payload)
            print(response)
            if response is None:
                logging.debug("Should not happen during testing")
            else:
                print("kip")
                await self._stream_writer.write(response)
                print("kip2")

        for handler in handlers:
            self._loop.create_task(handler(self, payload))
