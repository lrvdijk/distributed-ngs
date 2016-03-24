import asyncio
import argparse

from digs import db
from digs.manager import ManagerServerProtocol


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-h', '--hostname', default="localhost",
        help="Hostname to listen on, default localhost"
    )
    parser.add_argument(
        '-p', '--port', type=int, default=31415,
        help="Port to listen on, default 31415"
    )

    args = parser.parse_args()

    # TODO: database settings in configuration file?
    db.initialize_db("sqlite:///manager.db")

    loop = asyncio.get_event_loop()
    coro = loop.create_server(ManagerServerProtocol, args.hostname, args.port)

    server = loop.run_until_complete(coro)
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
