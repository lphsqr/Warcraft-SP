"""Package which imports all hero classes from all modules."""

# Warcraft imports
from warcraft._utilities import get_classes_from_package
from warcraft.entities import Hero

__all__ = (
    'get_heroes',
)


def get_heroes():
    """Yield all the heroes to use on the server.

    Automatically goes through every module in the ``heroes`` directory,
    importing every ``Hero`` subclass class from the modules.

    Ignores modules and classes with a leading underscore in their name.
    """
    for cls in get_classes_from_package(__path__):
        if issubclass(cls, Hero):
            yield cls
