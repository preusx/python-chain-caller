__version__ = '1.0.2'

from functools import reduce
from collections import UserDict, UserList


__all__ = [
    'resolve', 'this',
    'Resolvable', 'MagicCaller', 'ChainCaller', 'This',
]


class Resolvable:
    """Resolvable interface
    """

    def __resolve__(self, instance):
        """Resolve "magic" method. Named like this to avoid the naming
        collisions during resolving.

        Args:
            instance (object): An object to start resolving from

        Returns:
            object: The result of the resolving

        Raises:
            NotImplementedError: This is a n interface method, it must be
                implemented by the class children
        """
        raise NotImplementedError


def resolve(resolvable, obj):
    # Resolving list with a resolvables(mostly *args)
    if isinstance(resolvable, (tuple, list, UserList)):
        return [
            resolve(x, obj) if isinstance(x, Resolvable) else x
            for x in resolvable
        ]

    # Resolving dict with a resolvables(mostly *kwargs)
    if isinstance(resolvable, (dict, UserDict)):
        return {
            key: resolve(x, obj) if isinstance(x, Resolvable) else x
            for key, x in resolvable.items()
        }

    if not isinstance(resolvable, Resolvable):
        raise TypeError('First passed parameter must be a resolvable object, '
            'list or a dict that contain resolvables. Instead {type} object '
            'provided'.format(
                type=type(resolvable)
            ))

    return resolvable.__resolve__(obj)


def _caller(method):
    def call(self, *args, **kwargs):
        return self.__callmagic__(method, args, kwargs)

    return call


class MagicCaller:
    def __callmagic__(self, method, args, kwargs):
        """Any magic method will call this, and pass a called method name and
        call arguments.

        Args:
            method (str): A method name
            args (list|tuple): Caller *args list
            kwargs (dict): Caller *kwargs list

        Returns:
            any: Anything

        Raises:
            NotImplementedError: This is a n interface method, it must be
                implemented by the class children
        """
        raise NotImplementedError

    __call__      = _caller('__call__')
    __getattr__   = _caller('__getattribute__')
    __getitem__   = _caller('__getitem__')
    __setitem__   = _caller('__setitem__')
    __setitem__   = _caller('__setitem__')

    __contains__  = _caller('__contains__')
    __iter__      = _caller('__iter__')
    __next__      = _caller('__next__')
    __len__       = _caller('__len__')

    __add__       = _caller('__add__')
    __mul__       = _caller('__mul__')
    __sub__       = _caller('__sub__')
    __mod__       = _caller('__mod__')
    __pow__       = _caller('__pow__')

    __and__       = _caller('__and__')
    __or__        = _caller('__or__')
    __xor__       = _caller('__xor__')

    __div__       = _caller('__div__')
    __divmod__    = _caller('__divmod__')
    __floordiv__  = _caller('__floordiv__')
    __truediv__   = _caller('__truediv__')

    __lshift__    = _caller('__lshift__')
    __rshift__    = _caller('__rshift__')

    __lt__        = _caller('__lt__')
    __le__        = _caller('__le__')
    __gt__        = _caller('__gt__')
    __ge__        = _caller('__ge__')
    __eq__        = _caller('__eq__')
    __ne__        = _caller('__ne__')

    __neg__       = _caller('__neg__')
    __pos__       = _caller('__pos__')
    __invert__    = _caller('__invert__')

    __radd__      = _caller('__radd__')
    __rmul__      = _caller('__rmul__')
    __rsub__      = _caller('__rsub__')
    __rmod__      = _caller('__rmod__')
    __rpow__      = _caller('__rpow__')
    __rdiv__      = _caller('__rdiv__')
    __rdivmod__   = _caller('__rdivmod__')
    __rtruediv__  = _caller('__rtruediv__')
    __rfloordiv__ = _caller('__rfloordiv__')

    __rlshift__   = _caller('__rlshift__')
    __rrshift__   = _caller('__rrshift__')

    __rand__      = _caller('__rand__')
    __ror__       = _caller('__ror__')
    __rxor__      = _caller('__rxor__')


class ChainCaller(Resolvable, MagicCaller):
    """All the calls og this object will be stored and executed for some object
    later.
    You could do whatever you want to the instance of this object:
        - Any sorts of math
        - Item getters
        - Getting any attrubutes
        - Calling of the intenal methods

    Attributes:
        _chain (list): A chain of calls
    """
    _chain = []

    def __init__(self):
        self._chain = []

    def __callmagic__(self, method, args, kwargs):
        """On a magic method call add an info aboout it to a chain for further
        resolving

        Args:
            method (str): A method name
            args (list|tuple): Caller *args list
            kwargs (dict): Caller *kwargs list

        Returns:
            ChainCaller: Retuns self, for registering any further calls
        """
        self._chain.append((method, args, kwargs))

        return self

    def __resolve__(self, instance):
        def walker(obj, n):
            """Chain walker function

            Args:
                obj (object): Object, that we get in a previouse iteration
                n (tuple): A next caller tuple. Consist of:
                    0 - Attribute, that we need to call
                    1 - Arguments of the called attribute
                    2 - Keyword arguments of the called atttribute
                    All the arguments may contain a resolvers, that will be
                    resolved using first caller.

            Returns:
                object: A new object, from called method
            """
            attr = n[0]
            args = resolve(n[1], instance)
            kwargs = resolve(n[2], instance)
            # Wee need a hack here, when calling a `__getattribute__`
            if attr == '__getattribute__':
                try:
                    return getattr(obj, attr)(*args, **kwargs)
                except AttributeError as e:
                    attr = '__getattr__'

            return getattr(obj, attr)(*args, **kwargs)

        return reduce(walker, self._chain, instance)


class This(Resolvable, MagicCaller):
    def __resolve__(self, instance):
        """Just returns an instance

        Args:
            instance (object): Object to resolve from

        Returns:
            object: Instance that have been passed
        """
        return instance

    def __callmagic__(self, method, args, kwargs):
        """On a magic method call return new ChainCaller instance, and call
        a magic on that instance.

        Args:
            method (str): A method name
            args (list|tuple): Caller *args list
            kwargs (dict): Caller *kwargs list

        Returns:
            ChainCaller: Retuns ne instance of ChainCaller
        """
        # We cant call __getattribute__ on a ChainCaller, so we'r replacing it
        # with an __getattr__ call
        method = '__getattr__' if method == '__getattribute__' else method

        return getattr(ChainCaller(), method)(*args, **kwargs)


this = This()
