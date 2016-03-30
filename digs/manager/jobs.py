"""
Job queue management
====================

The distribution of jobs is distributed across workers using a RabbitMQ
message queue.
"""

import aioamqp


class JobManager:
    def __init__(self, routing_key):
        self.routing_key = routing_key

    async def schedule_job(self, ):
        transport, protocol = await aioamqp.connect()
        channel = await protocol.channel()




