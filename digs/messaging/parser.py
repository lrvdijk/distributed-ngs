import json
import collections

from digs.exc import InvalidActionError


class DigsParser:
    def __init__(self):
        self.actions = {}
        self.handlers = collections.defaultdict(list)

    def parse(self, data: bytes):
        data = data.decode()  # encoding should be utf-8

        action, json_data = data.strip().split(maxsplit=1)

        if action not in self.actions:
            raise InvalidActionError(
                "Trying to perform an unknown action '%s'" % action
            )

        payload = json.loads(json_data)
        # TODO: validate JSON schema for this action

        return action, payload, self.handlers[action]

    def define_action(self, action, json_schema):
        self.actions[action] = json_schema

    def register_handler(self, action, handler=None):
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
                self.handlers[action] = func

                return func

            return _register_handler
