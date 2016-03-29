from typing import Dict, Any
import logging
import json
import collections

from digs.messaging.actions import BaseAction
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
        self.actions = {}  # type: Dict[str, Any]
        self.handlers = collections.defaultdict(list)

    def parse(self, data: bytes):
        logger.debug("Start parsing incoming raw bytes: %s", data)

        # convert bytes to unicode, encoding should be utf-8
        data = data.decode()
        logger.debug("Unicode string: %s", data)

        # Check which action it tries to perform, and initialize the action
        # object (using values from the incoming JSON).
        action, json_data = data.strip().split(maxsplit=1)
        if action not in self.actions:
            raise InvalidActionError(
                "Trying to perform an unknown action '%s'" % action
            )

        action_class = self.actions[action]
        action_inst = action_class()
        action_inst.load_from_json(json.loads(json_data))

        logger.debug("Action class instance: %r", action_inst)

        return action_inst, self.handlers[action_inst.action]

    def define_action(self, action):
        assert issubclass(action, BaseAction)
        self.actions[action.action] = action

        # Return `action` so this function can be used as decorator
        return action

    def register_handler(self, action, handler=None):
        """Register a function as handler for a given action."""
        if action.action not in self.actions:
            raise InvalidActionError(
                "Trying to register a handler for an undefined "
                "action '%s'" % action
            )

        if handler is not None:
            self.handlers[action.action].append(handler)
        else:
            # Used as decorator, return wrapper function
            def _register_handler(func):
                self.handlers[action.action].append(func)

                return func

            return _register_handler
