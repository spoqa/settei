""":mod:`settei.base` --- Basic app object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.2.0

"""
import collections
import collections.abc
import enum
import functools
import pathlib
import re
import textwrap
import typing
import warnings

from pytoml import load
from typeguard import typechecked

__all__ = ('ConfigError', 'ConfigKeyError', 'ConfigTypeError',
           'Configuration', 'ConfigValueError', 'ConfigWarning',
           'config_object_property', 'config_property', 'get_union_types')


if hasattr(typing, 'UnionMeta'):
    def get_union_types(type_) -> bool:
        """Return a :class:`tuple` of the given :class:`~typing.Union`
        ``type_``'s parameters.

        >>> get_union_types(typing.Union[int, str, bool])
        (int, str, bool)

        If it's not an :class:`~typing.Union` type or even not a type
        it returns :const:`None`.

        .. versionadded:: 0.3.0

        """
        if isinstance(type_, typing.UnionMeta):
            return type_.__union_params__
elif hasattr(typing, '_Union'):
    # For older versions of typing
    def get_union_types(type_) -> bool:
        if type(type_) is typing._Union:
            return type_.__args__
else:
    # For newer versions of typing (>= Python 3.7)
    def get_union_types(type_) -> bool:
        if getattr(type_, '__origin__', None) is typing.Union and \
           hasattr(type_, '__args__'):
            return type_.__args__


class config_property:
    """Declare configuration key with type hints, default value, and
    docstring.

    :param key: the dotted string of key path.  for example ``abc.def`` looks
                up ``config['abc']['def']``
    :type key: :class:`str`
    :param cls: the allowed type of the configuration
    :type cls: :class:`type`
    :param docstring: optional documentation about the configuration.
                      it will be set to :attr:`__doc__` attribute
    :type docstring: :class:`str`
    :param default: keyword only argument.
                    optional default value used for missing case.
                    cannot be used with ``default_func`` at a time
    :param default_func: keyword only argument.
                         optional callable which returns a default value
                         for missing case.
                         it has to take an :class:`App` mapping, and return
                         a default value.
                         cannot be used with ``default`` at a time
    :type default_func: :class:`collections.abc.Callable`
    :param default_warning: keyword only argument.
                            whether to warn when default value is used.
                            does not warn by default.
                            this option is only available when ``default``
                            value is provided
    :type default_warning: :class:`bool`

    .. versionchanged:: 0.4.0

       Prior to 0.4.0, it had raised Python's built-in :exc:`KeyError` on
       missing keys, but since 0.4.0 it became to raise :exc:`ConfigKeyError`,
       a subtype of :exc:`KeyError`, instead.

       In the same manner, while prior to 0.4.0, it had raised Python's
       built-in :exc:`TypeError` when a configured value is not of a type
       it expects, but since 0.4.0 it became to raise :exc:`ConfigTypeError`
       instead. :exc:`ConfigTypeError` is also a subtype of :class:`TypeError`.

    """

    @typechecked
    def __init__(self, key: str, cls, docstring: str = None, **kwargs) -> None:
        self.key = key
        self.cls = cls
        self.__doc__ = docstring
        if 'default_func' in kwargs:
            if 'default' in kwargs:
                raise TypeError('default_func and default are mutually '
                                'exclusive')
            self.default_set = True
            self.default_value = True
            self.default_func = kwargs['default_func']
            self.default_warning = kwargs.get('default_warning', False)
        elif 'default' in kwargs:
            default = kwargs['default']
            self.default_set = True
            self.default_value = False
            self.default_func = lambda _: default
            self.default_warning = kwargs.get('default_warning', False)
        elif 'default_warning' in kwargs:
            raise TypeError('default_warning is only available when default '
                            'value is provided')
        else:
            self.default_set = False
            self.default_value = False
            self.default_func = None
            self.default_warning = False

    def __get__(self, obj, cls: typing.Optional[type] = None):
        if obj is None:
            return self
        default, value = self.get_raw_value(obj)
        if not default:
            value = self.convert_native_type(value)
            self.typecheck(value)
        return value

    def get_raw_value(self, obj) -> typing.Tuple[bool, object]:
        value = obj
        for key in self.key.split('.'):
            try:
                value = value[key]
            except KeyError:
                if self.default_set:
                    default = self.default_func(obj)
                    if self.default_warning:
                        warnings.warn(
                            "can't find {} configuration; use {}".format(
                                self.key, default
                            ),
                            ConfigWarning,
                            stacklevel=3
                        )
                    return True, default
                raise ConfigKeyError(key)
        return False, value

    def convert_native_type(self, value) -> typing.Any:
        cls = get_union_types(self.cls) or self.cls
        if isinstance(cls, type) and issubclass(cls, enum.Enum):
            try:
                return cls(value)
            except ValueError:
                raise ConfigTypeError(
                    'Invalid value {0} in {1!r}. Candidates are: {2}'.format(
                        value, cls, ', '.join(cls.__members__)
                    )
                )
        elif isinstance(cls, collections.abc.Iterable):
            enums = filter(lambda i: issubclass(i, enum.Enum), cls)
            non_enums = filter(lambda i: not issubclass(i, enum.Enum), cls)
            candidates = []
            for e in enums:
                try:
                    candidates.append(e(value))
                except ValueError:
                    pass
            if not candidates:
                if non_enums:
                    return value
                else:
                    raise ConfigTypeError(
                        'No matching value {0} for types: {1}'.format(
                            value, ', '.join([repr(r) for r in enums])
                        )
                    )
            elif len(candidates) == 1:
                return candidates[0]
            else:
                raise ConfigTypeError(
                    'Ambiguous enum type for value {0}: {1}'.format(
                        value, ', '.join([repr(r) for r in candidates])
                    )
                )
        return value

    def typecheck(self, value) -> None:
        union_types = get_union_types(self.cls)
        cls = self.cls if union_types is None else union_types
        if not isinstance(value, cls):
            raise ConfigTypeError(
                '{0} configuration must be {1}, not {2!r}'.format(
                    self.key, typing._type_repr(self.cls), value
                )
            )

    @property
    def docstring(self) -> str:
        """(:class:`str`) The propertly indented :attr:`__doc__` string."""
        return textwrap.dedent(self.__doc__).rstrip()

    def __repr__(self) -> str:
        return '{0.__module__}.{0.__qualname__}({1!r})'.format(
            type(self), self.key
        )


class config_object_property(config_property):
    """Similar to :class:`config_property` except it purposes to reprsent
    more complex objects than simple values.  It can be utilized as dependency
    injector.

    Suppose a field declared as::

        from werkzeug.contrib.cache import BaseCache

        class App(Configuration):
            cache = config_object_property('cache', BaseCache)

    Also a configuration:

    .. code-block:: toml

       [cache]
       class = "werkzeug.contrib.cache:RedisCache"
       host = "a.nodes.redis-cluster.local"
       port = 6379
       db = 0

    The above instantiates the following object::

        from werkzeug.contrib.cache import RedisCache
        RedisCache(host='a.nodes.redis-cluster.local', port=6380, db=0)

    There's a special field named ``*`` which is for positional arguments
    as well:

    .. code-block:: toml

       [cache]
       class = "werkzeug.contrib.cache:RedisCache"
       "*" = [
           "a.nodes.redis-cluster.local",
           6379,
       ]
       db = 0

    The above configuration is equivalent to the following Python code::

        from werkzeug.contrib.cache import RedisCache
        RedisCache('a.nodes.redis-cluster.local', 6380, db=0)

    By default it doesn't recursively evaluate.  For example, the following
    configuration:

    .. code-block:: toml

       [field]
       class = "a:ClassA"
       [field.value]
       class = "b:ClassB"
       [field.value.value]
       class = "c:ClassC"

    is evaluated to::

        from a import ClassA
        ClassA(value={'class': 'b:ClassB', 'value': {'class': 'c:ClassC'}})

    If ``recurse=True`` option is provided, it evaluates nested tables too::

        from a import ClassA
        from b import ClassB
        from c import ClassC

        ClassA(value=ClassB(value=ClassC()))

    :param key: the dotted string of key path.  for example ``abc.def`` looks
                up ``config['abc']['def']``
    :type key: :class:`str`
    :param cls: the allowed type of the configuration
    :type cls: :class:`type`
    :param docstring: optional documentation about the configuration.
                      it will be set to :attr:`__doc__` attribute
    :type docstring: :class:`str`
    :param recurse: whether to evaluate nested tables as well.
                    :const:`False` by default
    :type recurse: :class:`bool`
    :param default: keyword only argument.
                    optional default value used for missing case.
                    cannot be used with ``default_func`` at a time
    :param default_func: keyword only argument.
                         optional callable which returns a default value
                         for missing case.
                         it has to take an :class:`App` mapping, and return
                         a default value.
                         cannot be used with ``default`` at a time
    :type default_func: :class:`collections.abc.Callable`
    :param default_warning: keyword only argument.
                            whether to warn when default value is used.
                            does not warn by default.
                            this option is only available when ``default``
                            value is provided
    :type default_warning: :class:`bool`

    .. versionadded:: 0.4.0

    .. versionadded:: 0.5.0
       The ``recurse`` option.

    """

    CLASS_RE = re.compile(
        r'^(?P<path>(?:(?:^|\.)[^\d\W]\w*)+)?:'
        r'(?P<name>[^\d\W]\w*)$',
        re.UNICODE
    )

    @typechecked
    def __init__(self, key: str, cls, docstring: str = None,
                 recurse: bool = False, **kwargs) -> None:
        super().__init__(key=key, cls=cls, docstring=docstring, **kwargs)
        self.recurse = recurse

    def __get__(self, obj, cls: typing.Optional[type] = None):
        if obj is None:
            return self
        default, expression = self.get_raw_value(obj)
        if not default:
            if not isinstance(expression, collections.abc.Mapping):
                raise ConfigTypeError(
                    '{0!r} field must be a mapping, not {1}'.format(
                        self.key, typing._type_repr(type(expression))
                    )
                )
            elif 'class' not in expression:
                raise ConfigValueError(
                    '{0!r} field lacks "class" field'.format(self.key)
                )
            value = self.evaluate(expression)
            self.typecheck(value)
        return value

    def evaluate(self, expression) -> object:
        if not isinstance(expression, collections.abc.Mapping):
            return expression
        try:
            import_path = expression['class']
        except KeyError:
            return expression
        f = self.import_(import_path)
        args = expression.get('*', ())
        if isinstance(args, str) or \
           not isinstance(args, collections.abc.Sequence):
            raise ConfigValueError(
                '"*" field must be a list, not ' + repr(args)
            )
        kw = {k: v for k, v in expression.items() if k not in ('class', '*')}
        if self.recurse:
            args = map(self.evaluate, args)
            kw = {k: self.evaluate(v) for k, v in kw.items()}
        return f(*args, **kw)

    def import_(self, import_path: str) -> collections.abc.Callable:
        m = self.CLASS_RE.match(import_path)
        class_key = self.key + '.class'
        if not m:
            raise ConfigValueError(
                '{0!r} must be a valid import path '
                '(e.g. "module.path:cls_or_func"), not {1!r}'.format(
                    class_key, import_path
                )
            )
        path = m.group('path')
        v = __import__(path)
        keys = path.split('.')[1:]
        keys.append(m.group('name'))
        f = functools.reduce(getattr, keys, v)
        if not callable(f):
            raise ConfigValueError('{0!r} must refer to a callable, but {1!r} '
                                   'is not callable'.format(class_key, f))
        return f


class ConfigError(RuntimeError):
    """The base exception class for errors releated to :class:`Configuration`
    and :func:`config_property`.

    .. versionadded:: 0.4.0

    """


class ConfigKeyError(KeyError, ConfigError):
    """An exception class rises when there's no a configuration key.
    A subtype of :exc:`ConfigError` and :exc:`KeyError`.

    .. versionadded:: 0.4.0

    """


class ConfigValueError(ValueError, ConfigError):
    """An execption class rises when the configured value is somewhat
    invalid.

    .. versionadded:: 0.4.0

    """


class ConfigTypeError(TypeError, ConfigError):
    """An exception class rises when the configured value is not of a type
    the field expects.

    .. versionadded:: 0.4.0

    """


class ConfigWarning(RuntimeWarning):
    """Warning category which raised when a default configuration is used
    instead due to missing required configuration.

    """


class Configuration(collections.abc.Mapping):
    """Application instance with its settings e.g. database.  It implements
    read-only :class:`~collections.abc.Mapping` protocol as well, so you
    can treat it as a dictionary of string keys.

    .. versionchanged:: 0.4.0

       Prior to 0.4.0, it had raised Python's built-in :exc:`KeyError` on
       missing keys, but since 0.4.0 it became to raise :exc:`ConfigKeyError`,
       a subtype of :exc:`KeyError`, instead.

    """

    @classmethod
    def from_file(cls, file) -> 'Configuration':
        """Load settings from the given ``file`` and instantiate an
        :class:`Configuration` instance from that.

        :param file: the file object that contains TOML settings
        :return: an instantiated configuration
        :rtype: :class:`Configuration`

        """
        return cls(load(file))

    @classmethod
    @typechecked
    def from_path(cls, path: pathlib.Path) -> 'Configuration':
        """Load settings from the given ``path`` and instantiate an
        :class:`Configuration` instance from that.

        :param path: the file path that contains TOML settings
        :type path: :class:`pathlib.Path`
        :return: an instantiated configuration
        :rtype: :class:`Configuration`

        """
        if not path.is_file():
            raise FileNotFoundError('file not found: {!s}'.format(path))
        with path.open() as f:
            return cls.from_file(f)

    @typechecked
    def __init__(self, config: typing.Mapping[str, object] = {}, **kwargs):
        self.config = dict(config, **kwargs)

    def __len__(self) -> int:
        return len(self.config)

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.config)

    def __getitem__(self, key: str):
        if isinstance(key, str):
            try:
                return self.config[key]
            except KeyError:
                pass
        raise ConfigKeyError(key)

    def __repr__(self) -> str:
        return '{0.__module__}.{0.__qualname__}({1!r})'.format(
            type(self), self.config
        )
