import argparse

from digs import conf
from digs.common.utils import get_random_central_server
from digs.exc import ConfigurationError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--conf', required=False, default="",
        help="Provide additional configuration file, on top of the default "
             "ones."
    )
    parser.add_argument(
        '-d', '--debug', action="store_true", default=False,
        help="Enable debug mode."
    )

    args = parser.parse_args()

    if 'worker' not in conf.settings:
        raise ConfigurationError("The configuration file does not have a "
                                 "'worker' section.")
    worker_settings = conf.settings['worker']

    rabbitmq_settings = {
        key.replace("rabbitmq.", ""): worker_settings[key]
        for key in worker_settings if key.startswith("rabbitmq.")
        }

    rabbitmq_settings['host'] = get_random_central_server()
    rabbitmq_settings['port'] = 5672



if __name__ == '__main__':
    main()

