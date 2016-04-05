import os
import configparser

paths = [
    os.path.expanduser('~/.config/digs/digs.conf'),
    os.path.realpath(os.path.join(os.path.dirname(__file__), '..',
                                  'digs.conf'))
]

settings = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())

settings.read(paths)
