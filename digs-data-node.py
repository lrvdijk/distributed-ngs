import argparse
import asyncio
import logging

from digs.data_node.data_node import DataNode
from digs.data_node.server import DataNodeServerProtocol

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    # TODO: define command line arguments

    args = parser.parse_args()
    # TODO: write data node code
    node = DataNode()
    node.create_database("sqlite:///data_node.db")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-hn', '--hostname', default="localhost",
        help='Hostname to listen on, default localhost'
    )
    parser.add_argument(
        '-p', '--port', type=int, default=5000,
        help="Port to listen on, default 5000"
    )

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    coro = loop.create_server(DataNodeServerProtocol, args.hostname, args.port)

    server = loop.run_until_complete(coro)
    # loop.run_until_complete(server.wait_closed())
    print("Serving on {}".format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    print("aap")

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()
