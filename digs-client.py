import argparse
import asyncio
import logging
import warnings

from digs import conf
from digs.common.actions import JobRequest, Job
from digs.common.utils import get_random_central_server
from digs.exc import ConfigurationError
from digs.messaging import persistent

logging.basicConfig(level=logging.INFO)


class MAFFTJob(Job):
    sequences = int


async def send_job_request(publisher):
    # Enter correct file ID for sequences data
    job = MAFFTJob(program_name='mafft', sequences=1)
    req = JobRequest(job=job)

    return await publisher.publish(str(req), "digs.messages",
                                   "action.{}".format(req.action))


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

    if args.conf:
        conf.settings.read(args.conf)

    loop = asyncio.get_event_loop()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        warnings.filterwarnings("always", category=ResourceWarning)
        loop.set_debug(True)

    if 'client' not in conf.settings:
        raise ConfigurationError("The configuration file does not have a "
                                 "'client' section.")
    client_settings = conf.settings['client']

    rabbitmq_settings = {
        key.replace("rabbitmq.", ""): client_settings[key]
        for key in client_settings if key.startswith("rabbitmq.")
    }

    rabbitmq_settings['host'] = get_random_central_server()

    coro = persistent.create_publisher(**rabbitmq_settings)
    publisher = loop.run_until_complete(coro)
    loop.run_until_complete(send_job_request(publisher))
    loop.run_until_complete(persistent.wait_closed())

    loop.close()


if __name__ == '__main__':
    main()
