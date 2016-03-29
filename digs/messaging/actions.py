import json
import copy


class ActionsMeta(type):
    """This metaclass collects the attributes to be serialized into JSON for a
    protocol action."""

    def __new__(mcs, name, bases, attrs):
        declared_fields = {}

        for key, value in attrs.items():
            if value in [str, int, list, dict] or isinstance(value,
                                                             ActionsMeta):
                declared_fields[key] = value

            if key == '__action__':
                attrs['action'] = attrs.pop('__action__')

        attrs['declared_fields'] = declared_fields
        new_class = super().__new__(mcs, name, bases, attrs)

        # Traverse base classes using Method Resolution Order
        # to properly support overriding actions
        declared_fields = {}
        for base in reversed(new_class.__mro__):
            if hasattr(base, "declared_fields") and base.declared_fields:
                declared_fields.update(base.declared_fields)

            # Remove attributes removed by any subclasses
            for key, value in base.__dict__.items():
                if value is None and key in declared_fields:
                    declared_fields.pop(key)

        new_class.declared_fields = declared_fields

        return new_class


class BaseAction:
    """Base class for an action, without any assumption of the
    `declared_fields` attribute."""

    declared_fields = None

    def __init__(self, *args, **kwargs):
        self.fields = copy.deepcopy(self.declared_fields)
        self.values = {}

        for field, field_type in self.fields.items():
            if field in kwargs:
                self.values[field] = self._ensure_type(
                    field_type, kwargs[field])

        if not hasattr(self, 'action'):
            raise TypeError("Defined an action '{!r}' without specifying an "
                            "action name. Try setting __action__ or "
                            "base_action.".format(self.__class__))

    def _ensure_type(self, field_type, value):
        if field_type in [str, int, list, dict]:
            return field_type(value)
        else:
            if isinstance(value, field_type):
                return value
            else:
                raise TypeError(
                    "Object {!r} is not an instance of {!r}".format(
                        value, field_type)
                )

    def to_json(self):
        values = {}
        for field, value in self.values.items():
            if isinstance(value, BaseAction):
                value = value.to_json()

            values[field] = value

        return json.dumps(values)

    def serialize(self):
        return "{} {}\n".format(self.action, self.to_json())

    def load_from_json(self, json_data):
        keys_loaded = []
        for key, value in json_data.items():
            if key not in self.fields:
                raise TypeError(
                    "The key '{}' does not belong in the JSON data for "
                    "action '{}'".format(key, self.action)
                )

            field_type = self.fields[key]

            if issubclass(field_type, BaseAction):
                inst = field_type()
                value = inst.load_from_json(value)
            else:
                value = field_type(value)

            keys_loaded.append(key)
            self.values[key] = value

        empty_fields = set(self.fields.keys()) - set(keys_loaded)
        if len(empty_fields) > 0:
            raise TypeError(
                "JSON data did not contain any data for the "
                "following fields: {}".format(
                    ", ".join(empty_fields))
            )

        return self


class Action(BaseAction, metaclass=ActionsMeta):
    """Combine the functionality of the base action class with the
    declarative functionality of the metaclass."""
