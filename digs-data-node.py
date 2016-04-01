import argparse
import asyncio
import logging

from digs.data_node.server import DataNodeTransientProtocol


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    # TODO: define command line arguments

    args = parser.parse_args()
    # TODO: write data node code
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-hn', '--hostname', default="localhost",
        help='Hostname to listen on, default localhost'
    )
    parser.add_argument(
        '-p', '--port', type=int, default=5001,
        help="Port to listen on, default 5001"
    )

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    reader = asyncio.StreamReader(loop=loop)
    coro = loop.create_server(DataNodeTransientProtocol, args.hostname, args.port)

    server = loop.run_until_complete(coro)
    # loop.run_until_complete(server.wait_closed())
    print("Serving on {}".format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()
