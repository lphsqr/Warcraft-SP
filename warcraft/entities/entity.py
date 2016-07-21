"""Module with the base class for all Warcraft entities."""

# Python 3 imports
import math

# Warcraft imports
from warcraft._utilities import ClassProperty

__all__ = (
    'Entity',
)


class Entity:
    """Base class for all Warcraft entities.

    Implements the following common class properties:

    - ``class_id`` (:class:`str`):
        An unique identifier for the entity class. Automatically
        retrieved from the class's ``__qualname__``.
    - ``name`` (:class:`str`)
        The display name of the class. Automatically retrieved
        from the class's ``__name__``, replacing all the underscores
        with spaces. If underscores or other disallowed characters in
        class's name are needed, this should be overridden with
        a string class attribute.
    - ``description`` (:class:`str`):
        A short description of the skill. Automatically retrieved
        from the class's ``__doc__``.
    - ``max_level`` (:class:`int`):
        Maximum level of the class. Defaults to ``math.inf``.
    - ``required_level`` (:class:`int`):
        Required level for the entity before it can be used.
        Defaults to ``0``.

    These can all be overridden by a subclass with class attributes.

    Also implements :attr:`level` attribute and :meth:`on_max_level`
    method for managing the instance's current level.
    """

    @ClassProperty
    def class_id(cls):
        return cls.__qualname__

    @ClassProperty
    def name(cls):
        return cls.__name__.replace('_', ' ')

    @ClassProperty
    def description(cls):
        return cls.__doc__

    max_level = math.inf
    required_level = 0

    def __init__(self, level=0):
        """Initialize the entity.

        :param int level:
            Initial level of the entity
        """
        self._level = level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if value < 0:
            raise ValueError(
                "Attempt to set entity's level to a negative value.")
        if self.max_level < value:
            raise ValueError(
                "Attempt to set entity's level to a value larger than it's max_level.")
        self._level = value

    def on_max_level(self):
        """Check if an entity is on its maximum level.

        :returns bool:
            ``True`` if the entity is on its max level, else ``False``
        """
        return self.level == self.max_level
