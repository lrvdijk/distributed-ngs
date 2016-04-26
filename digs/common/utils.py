import asyncio
import random

from digs.conf import settings


def get_random_central_server():
    if 'servers' not in settings:
        return None

    server_settings = settings['servers']
    servers = [server_settings[key] for key in server_settings if
               key.startswith("central.server.")]

    return random.choice(servers)


async def connect_to_random_central_server():
    if 'servers' not in settings:
        return None

    server_settings = settings['servers']
    servers = [server_settings[key] for key in server_settings if
               key.startswith("central.server.")]

    for server in random.shuffle(servers):
        try:
            return await asyncio.open_connection(server, 31415)
        except OSError:
            continue

    raise IOError("No central servers available!")
