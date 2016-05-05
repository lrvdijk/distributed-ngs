import copy
import json


class SerializableMeta(type):
    """This metaclass collects the attributes to be serialized into JSON."""

    def __new__(mcs, name, bases, attrs):
        declared_fields = {}

        for key, value in attrs.items():
            if value in [str, int, list, dict] or isinstance(value,
                                                             SerializableMeta):
                declared_fields[key] = value

        attrs['declared_fields'] = declared_fields
        new_class = super().__new__(mcs, name, bases, attrs)

        # Traverse base classes using Method Resolution Order
        # to properly support overriding fields
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


class BaseSerializable:
    """This is a base class for any JSON serializable object. It does not
    make any assumption how declared_fields are filled. This class can be
    used in combination with :class:`SerializableMeta` to automatically fill
    `declared_fields` from defined class attributes.

    .. seealso::
        :class:`SerializableMeta`
    """
    declared_fields = None

    def __init__(self, *args, **kwargs):
        self.fields = copy.deepcopy(self.declared_fields)
        self.values = {}

        for field, field_type in self.fields.items():
            if field in kwargs:
                self.values[field] = self._ensure_type(
                    field_type, kwargs[field])

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

    def get_values(self):
        values = {}
        for field, value in self.values.items():
            if isinstance(value, BaseSerializable):
                value = value.get_values()

            values[field] = value

        return values

    def to_json(self):
        return json.dumps(self.get_values())

    def load_from_json(self, json_data):
        keys_loaded = []
        for key, value in json_data.items():
            if key in self.fields:
                field_type = self.fields[key]
            else:
                field_type = str

            if issubclass(field_type, BaseSerializable):
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

    def __getitem__(self, item):
        if item not in self.fields:
            raise KeyError(
                "'{}' does not contain a field '{}'".format(
                    self.__class__.__name__, item)
            )

        return self.values.get(item, None)

    def __setitem__(self, key, value):
        self.values[key] = value


class Serializable(BaseSerializable, metaclass=SerializableMeta):
    """Combines the functionality of `BaseSerializable` and
    `SerializableMeta` to be able define JSON schemas in a declaritive
    manner.

    .. seealso::
        :class:`BaseSerializable`, :class:`SerializableMeta`
    """
