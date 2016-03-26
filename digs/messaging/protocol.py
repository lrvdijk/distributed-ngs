import logging
import json
import collections

from digs.exc import InvalidActionError

logger = logging.getLogger(__name__)


class DigsProtocolParser:
    """The digs protocol is defined as follows:

        action json_payload\n

    To summarize: it's a line based protocol where the first word defines the
    action to perform, and each action has its own defined JSON schema,
    where additional parameters can be given.
    """

    def __init__(self):
        self.actions = {}
        self.handlers = collections.defaultdict(list)

    def parse(self, data):
        logger.debug("Start parsing incoming raw bytes: %b", data)
        data = data.decode()  # encoding should be utf-8
        logger.debug("Unicode string: %s", data)
        action, json_data = data.strip().split(maxsplit=1)

        if action not in self.actions:
            raise InvalidActionError(
                "Trying to perform an unknown action '%s'" % action
            )

        payload = json.loads(json_data)
        logger.debug("JSON payload: %s", payload)

        # TODO: validate JSON schema for this action
        return action, payload, self.handlers[action]

    def define_action(self, action, json_schema):
        self.actions[action] = json_schema

    def register_handler(self, action, handler=None):
        """Register a function as handler for a given action."""
        if action not in self.actions:
            raise InvalidActionError(
                "Trying to register a handler for an undefined "
                "action '%s'" % action
            )

        if handler is not None:
            self.handlers[action].append(handler)
        else:
            # Used as decorator, return wrapper function
            def _register_handler(func):
                self.handlers[action].append(func)

                return func

            return _register_handler
