
class InvalidActionError(Exception):
    pass


class MessagingError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class InvalidChunkSizeError(Exception):
    pass


class NotEnoughSpaceError(Exception):
    pass


class UnknownHash(Exception):
    pass
