"""
Job queue management
====================

Jobs are distributed across workers using a RabbitMQ message queue.
"""

from digs.messaging.persistent import get_channel
from digs.common.actions import Job, PerformJob
from digs.conf import settings


class JobQueue:
    """Creates and manages a RabbitMQ exchange where jobs will be send to."""

    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.settings = settings['manager']

    async def queue_job(self, job: Job):
        channel = await get_channel(self.settings)
        await channel.exchange_declare(self.exchange_name, 'topic',
                                       durable=True)

        action = PerformJob(job=job)
        topic = 'jobs.{}'.format(job.program_name)
        await channel.publish(str(action), self.exchange_name, topic)



