import random

from digs.conf import settings


def get_random_central_server():
    if 'client' not in settings:
        return None

    client_settings = settings['client']
    servers = [client_settings[key] for key in client_settings if
               key.startswith("central.server.")]

    return random.choice(servers)
