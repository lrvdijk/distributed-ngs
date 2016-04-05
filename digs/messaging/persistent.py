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
from aioamqp.protocol import AmqpProtocol
from aioamqp.channel import Channel

from digs.exc import MessagingError
from digs.messaging.actions import Action
from digs.messaging.protocol import BaseProtocol, DigsProtocolParser

logger = logging.getLogger(__name__)


class PersistentProtocol(BaseProtocol):
    """An instance of this class is created each time a message is received
    through the RabbitMQ queue.

    It provides some helper functions for sending and parsing actions."""

    def __init__(self, channel: Channel, body, envelope, properties,
                 loop=None):
        self.channel = channel
        self.body = body
        self.envelope = envelope
        self.properties = properties

        self._loop = loop

    @abstractproperty
    def parser(self) -> DigsProtocolParser:
        pass

    async def send_action(self, action: Action):
        """If the received action contains a `reply_to` property,
        this function can be used to send an action to this corresponding
        RabbitMQ queue.

        :param action: The action to be sent as reply
        """

        if not self.properties.reply_to:
            raise MessagingError(
                "Unable to send action {!r}, no reply to address "
                "known.".format(action)
            )

        return await self.channel.basic_publish(
            str(action),
            exchange_name='',
            routing_key=self.properties.reply_to,
            properties={
                'correlation_id': self.properties.correlation_id
            }
        )

    async def process(self):
        data = str(self.body)
        logger.debug("process(): data %s", data)

        if len(data.strip()) == 0:
            return

        action, handlers = self.parser.parse(data)

        for handler in handlers:
            logger.debug("Scheduling handler %r", handler)
            self._loop.create_task(handler(self, action))


class PersistentListener:
    def __init__(self, transport: asyncio.BaseTransport,
                 protocol: AmqpProtocol, channel: Channel,
                 protocol_factory=PersistentProtocol, loop=None):

        self.transport = transport
        self.protocol = protocol
        self.protocol_factory = protocol_factory
        self._loop = loop if loop is not None else asyncio.get_event_loop()

        self.channel = channel

    async def listen_for(self, exchange, topic):
        await self.channel.exchange(exchange, type_name='topic')

        # Exclusive queue with random name for this listener
        queue = await self.channel.queue_declare(exclusive=True)

        # Bind queue to messages exchange, and listen to messages of given
        # topic
        await self.channel.queue_bind(queue['queue'], exchange,
                                      routing_key=topic)

        return await self.channel.basic_consume(self._on_message,
                                                queue['queue'])

    async def _on_message(self, channel, body, envelope, properties):
        protocol = self.protocol_factory(channel, body, envelope,
                                         properties, self._loop)

        self._loop.create_task(protocol.process())

    async def wait_closed(self):
        if self.protocol.is_open:
            await self.protocol.close()

        if not self.transport.is_closing():
            self.transport.close()

async def create_persistent_listener(protocol_factory=PersistentProtocol,
                                     *args, loop=None, **kwargs):
    """Connect to RabbitMQ server"""
    transport, protocol = await aioamqp.connect(*args, **kwargs)
    channel = await protocol.channel()

    return PersistentListener(transport, protocol, channel,
                              protocol_factory, loop)
