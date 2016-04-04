import asyncio
import argparse
import logging
import warnings

from digs import db, conf
from digs.messaging import persistent
from digs.manager import ManagerTransientProtocol

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--conf', required=False, default="",
        help="Provide additional configuration file, on top of the default "
             "ones."
    )
    parser.add_argument(
        '-hn', '--hostname', default="",
        help="Hostname to listen on, overrides anything in the configuration"
             " and defaults to localhost."
    )
    parser.add_argument(
        '-p', '--port', type=int, default=-1,
        help="Port to listen on, overrides anything in the configuration "
             "file and defaults to 31415."
    )
    parser.add_argument(
        '-d', '--debug', action="store_true", default=False,
        help="Enable debug mode."
    )

    args = parser.parse_args()

    if args.conf:
        conf.settings.read(args.conf)

    hostname = "127.0.0.1"
    if args.hostname:
        hostname = args.hostname
    elif 'hostname' in conf.settings['manager']:
        hostname = conf.settings['manager']['hostname']

    port = 31415
    if args.port > 0:
        port = args.port
    elif 'port' in conf.settings['manager']:
        port = conf.settings['manager'].getint('port')

    # Connect to database
    db.initialize_db(conf.settings['manager']['sqlalchemy.url'])

    # Start the event loop
    loop = asyncio.get_event_loop()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        warnings.filterwarnings("always", category=ResourceWarning)
        loop.set_debug(True)

    coro = loop.create_server(ManagerTransientProtocol, hostname, port)
    server = loop.run_until_complete(coro)

    persistent_msg_listener = persistent.persistent_messages_listener(
        conf.settings['manager'], )

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
