import argparse
import asyncio
import logging
import warnings

from digs import conf
from digs.manager import ManagerTransientProtocol, ManagerPersistentProtocol
from digs.messaging import persistent
from digs import conf
from digs.manager import db, ManagerTransientProtocol, ManagerPersistentProtocol
from digs.exc import ConfigurationError

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

    if 'manager' not in conf.settings:
        raise ConfigurationError("The configuration file does not have a "
                                 "'manager' section.")
    manager_settings = conf.settings['manager']

    hostname = ""
    port = 31415
    if args.hostname:
        hostname = args.hostname
    elif 'hostname' in manager_settings:
        hostname = manager_settings['hostname']

    if args.port > 0:
        port = args.port
    elif 'port' in manager_settings:
        port = manager_settings.getint('port')

    # Connect to database
    db.initialize_db(manager_settings['sqlalchemy.url'])

    # Start the event loop
    loop = asyncio.get_event_loop()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        warnings.filterwarnings("always", category=ResourceWarning)
        loop.set_debug(True)


    rabbitmq_settings = {
        key.replace("rabbitmq.", ""): manager_settings[key]
        for key in manager_settings if key.startswith("rabbitmq.")
    }

    if 'port' in rabbitmq_settings:
        rabbitmq_settings['port'] = int(rabbitmq_settings['port'])

    coro = persistent.create_persistent_listener(ManagerPersistentProtocol,
                                                 **rabbitmq_settings)
    persistent_listener = loop.run_until_complete(coro)
    loop.create_task(persistent_listener.listen_for(
        "digs.messages", "action.*", 'central_queue'))
    coro = loop.create_server(ManagerTransientProtocol, hostname, port)
    server = loop.run_until_complete(coro)

    print("Serving on {}".format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.run_until_complete(persistent.wait_closed())

    loop.close()

if __name__ == '__main__':
    main()
