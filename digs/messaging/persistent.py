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
from aioamqp.envelope import Envelope
from aioamqp.channel import Channel

from digs.exc import MessagingError
from digs.messaging.actions import Action
from digs.messaging.protocol import BaseProtocol, DigsProtocolParser

logger = logging.getLogger(__name__)
rabbitmq_connection = {}


class PersistentProtocol(BaseProtocol):
    """An instance of this class is created each time a message is received
    through the RabbitMQ queue.

    It provides some helper functions for sending and parsing actions."""

    def __init__(self, channel: Channel, body, envelope: Envelope,
                 properties, loop=None):
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
        try:
            logger.debug("process(): data %s", self.body)

            if len(self.body.strip()) == 0:
                return

            action, handler = self.parser.parse(self.body)

            logger.debug("Scheduling handler %r", handler)
            await handler(self, action)
            logger.debug("Successfully finished handler %r, sending ack" %
                         handler)
            await self.channel.basic_client_ack(self.envelope.delivery_tag)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        except Exception:
            logger.exception("Error while handling an action coming through "
                             "the persistent channel.")


class PersistentListener:
    def __init__(self, transport: asyncio.BaseTransport,
                 protocol: AmqpProtocol, channel: Channel,
                 protocol_factory=PersistentProtocol, loop=None):

        self.transport = transport
        self.protocol = protocol
        self.protocol_factory = protocol_factory
        self._loop = loop if loop is not None else asyncio.get_event_loop()

        self.channel = channel

    async def listen_for_topic(self, exchange, topic, queue_name=''):
        await self.channel.exchange(exchange, type_name='topic')

        # Exclusive queue with random name for this listener
        durable = queue_name != ''
        queue = await self.channel.queue_declare(queue_name=queue_name,
                                                 durable=durable)

        # Bind queue to messages exchange, and listen to messages of given
        # topic
        await self.channel.queue_bind(queue['queue'], exchange,
                                      routing_key=topic)

        return await self.channel.basic_consume(self._on_message,
                                                queue['queue'])

    async def basic_consume(self, queue_name):
        return await self.channel.basic_consume(self._on_message, queue_name)

    async def _on_message(self, channel, body, envelope, properties):
        protocol = self.protocol_factory(channel, body, envelope,
                                         properties, self._loop)

        self._loop.create_task(protocol.process())


async def create_persistent_listener(protocol_factory, *args, loop=None,
                                     **kwargs):
    """Connect to RabbitMQ server.

    This function accepts the same parameters als the `aioamqp.connect`
    function, with the exception of `protocol_factory`. This parameter has a
    different meaning in this function.

    :param protocol_factory: When a new messages arrives, the protocol
    defines how to handle this message. This parameter should be a callable
    which returns the protocol instance.
    :type protocol_factory: PersistentProtocol
    :param loop: Optionally specify which event loop to use
    """

    if not rabbitmq_connection:
        transport, protocol = await aioamqp.connect(*args, **kwargs)
        rabbitmq_connection['transport'] = transport
        rabbitmq_connection['protocol'] = protocol

    channel = await rabbitmq_connection['protocol'].channel()
    channel.queue_declare("jobs.mafft")

    return PersistentListener(rabbitmq_connection['transport'],
                              rabbitmq_connection['protocol'], channel,
                              protocol_factory, loop)


class PersistentPublisher:
    def __init__(self, transport: asyncio.BaseTransport,
                 protocol: AmqpProtocol, channel: Channel, loop=None):
        self.transport = transport
        self.protocol = protocol
        self.channel = channel

        self.protocol_factory = None
        self.reply_queue = None
        self._loop = loop

    async def with_reply_queue(self, protocol_facotory):
        result = await self.channel.queue_declare(queue_name='',
                                                  exclusive=True)

        # TODO

    async def publish(self, body, exchange_name, routing_key,
                      expect_reply=False, persistent=True):
        properties = None
        if persistent:
            properties = {
                'delivery_mode': 2
            }

        if expect_reply:
            if not self.reply_queue:
                raise MessagingError(
                    "Trying to publish a message which expects a message, "
                    "but the reply queue has not yet been set up. Please "
                    "call PersistentPublisher.with_reply_queue."
                )

            # TODO

        return await self.channel.basic_publish(
            body, exchange_name, routing_key,
            properties
        )


async def create_publisher(*args, loop=None, **kwargs):
    if not rabbitmq_connection:
        transport, protocol = await aioamqp.connect(*args, **kwargs)
        rabbitmq_connection['transport'] = transport
        rabbitmq_connection['protocol'] = protocol

    channel = await rabbitmq_connection['protocol'].channel()

    return PersistentPublisher(rabbitmq_connection['transport'],
                               rabbitmq_connection['protocol'], channel,
                               loop=loop)


async def wait_closed():
    if rabbitmq_connection:
        transport = rabbitmq_connection['transport']
        protocol = rabbitmq_connection['protocol']

        if protocol.is_open:
            await protocol.close()

        if not transport.is_closing():
            transport.close()
