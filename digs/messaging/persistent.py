"""
Persistent messaging through a RabbitMQ message queue
=====================================================

This module provides an easy API to build a persistent messaging system
using a RabbitMQ message queue.
"""

import asyncio
import logging
from abc import abstractproperty

import aioamqp
from aioamqp.channel import Channel

from digs.messaging.protocol import BaseProtocol, DigsProtocolParser

logger = logging.getLogger(__name__)


class PersistentProtocol(BaseProtocol):
    def __init__(self, channel: Channel, exchange_name, topic, loop=None):
        self.channel = channel
        self.default_exchange = exchange_name
        self.default_topic = topic
        self._loop = loop or asyncio.get_event_loop()

    @abstractproperty
    def parser(self) -> DigsProtocolParser:
        pass

    def send_action(self, action, exchange=None, topic=None):
        exchange = exchange if exchange is not None else self.default_exchange
        topic = topic if topic is not None else self.default_topic

        # TODO
        self.channel.basic_publish()

    async def process(self, channel, data, envelope, properties):
        logger.debug("process(): data %s", data)
        action, handlers = self.parser.parse(data)

        for handler in handlers:
            self._loop.create_task(handler(self, action))


async def get_channel(settings) -> Channel:
    """Connect to the RabbitMQ server and create a channel.

    :param settings: dict like instance containing the rabbit mq server
    settings
    :type settings: dict
    """
    transport, protocol = aioamqp.connect(
        settings.get('rabbitmq_host', 'localhost'),
        int(settings.get('rabbitmq_port', 5672))
    )

    return await protocol.channel()


async def persistent_messages_listener(settings, topic, protocol_factory,
                                       loop=None):
    channel = await get_channel(settings)
    await channel.exchange(settings['messages_exchange_name'],
                           type_name='topic')

    # Exclusive queue with random name for this listener
    queue = await channel.queue_declare(exclusive=True)

    # Bind queue to messages exchange, and listen to messages of given topic
    await channel.queue_bind(
        queue['queue'], settings['messages_exchange_name'], topic)

    protocol = protocol_factory(channel, settings['messages_exchange_name'],
                                topic, loop)

    while True:
        try:
            await channel.basic_consume(protocol.process, queue['queue'])
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.debug("Persistent messaging listener cancelled")
            break
        except Exception:
            logger.exception("Error while handling data from the client")
