"""Utility functions/classes needed internally by the plugin."""

# Python 3 imports
import importlib
import inspect
import pkgutil

__all__ = (
    'ClassProperty',
)


class ClassProperty:
    """Read-only property for classes instead of instances.

    Acts as a combination of :func:`property` and :func:`classmethod`
    to create properties for classes.
    The recommended usage of :class:`ClassProperty` is as a decorator:

    .. code-block:: python

        class My_Class:

            @ClassProperty
            def name(cls):
                return cls.__name__.replace('_', ' ')

        obj = My_Class()

        print('Accessed through the class:', My_Class.name)
        print('Accessed through the object:', obj.name)

        class My_Subclass_One(My_Class):
            pass

        class My_Subclass_Two(My_Class):
            # Override the classproperty
            name = 'My_Subclass: 2'

        print('Accessed through subclass 1:', My_Subclass_One.name)
        print('Accessed through subclass 2:', My_Subclass_Two.name)

    Output:

    .. code-block:: none

        Accessed through the class: My Class
        Accessed through the object: My Class
        Accessed through subclass 1: My Subclass One
        Accessed through subclass 2: My_Subclass: 2
    """

    def __init__(self, fget=None, doc=None):
        """Initialize the class property with a get function.

        :param callable|None fget:
            Function to call when the property is read
        :param str|None doc:
            Docstring, automatically copied from ``fget`` if None
        """
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.fget = fget
        self.__doc__ = doc

    def __get__(self, obj=None, type_=None):
        """Call :attr:`fget` when the class property is read.

        :param object obj:
            Object accessing the class property (can be None)
        :param type type_:
            Class accessing the class property

        If ``type_`` is ``None`` but an object was provided, ``type_``
        will be recieved from ``type(obj)``.
        """
        if type_ is None and obj is not None:
            type_ = type(obj)
        return self.fget(type_)


def get_classes_from_module(module, *, private=False, imported=False):
    """Yield classes from a module.

    :param module module:
        Module to get the classes from
    :param bool private:
        Yield classes prefixed with an underscore
    :param bool imported:
        Yield classes imported from other modules
    """
    for obj_name, obj in inspect.getmembers(module):
        if not private and obj_name.startswith('_'):
            continue
        if not inspect.isclass(obj):
            continue
        if not imported and obj.__module__ != module.__name__:
            continue
        yield obj


def import_submodules(package, *, private_modules=False, recursive=True):
    """Yield classes from all modules of a package.

    :param module package:
        Package to get the classes from
    :param bool private_modules:
        Seek for classes inside of modules with leading underscore
    :param bool recursive:
        Recursively also get classes from subpackages
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        if not private_modules and module_name.startswith('_'):
            continue
        full_name = package.__name__ + '.' + module_name
        module = importlib.import_module(full_name)
        if not is_pkg:
            yield module
        elif recursive:
            yield from import_submodules(module)
