from digs.messaging.serialization import BaseSerializable, SerializableMeta


class ActionMeta(SerializableMeta):
    def __new__(mcs, name, bases, attrs):
        if attrs['__module__'] is not __name__ and '__action__' not in attrs:
            raise TypeError(
                "Defined an action '{}' without specifying an "
                "action name. Please set the __action__ attribute.".format(
                    name)
            )

        action = None
        if '__action__' in attrs:
            action = attrs.pop('__action__')

        new_class = super().__new__(mcs, name, bases, attrs)
        new_class.action = action

        return new_class


class BaseAction(BaseSerializable):
    """Base class for an action, without any assumption of the
    `declared_fields` attribute."""

    action = None

    def __str__(self):
        return "{} {}\n".format(self.action, self.to_json())


class Action(BaseAction, metaclass=ActionMeta):
    """Combine the functionality of the base action class with the
    declarative functionality of the metaclass."""
