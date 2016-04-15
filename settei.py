"""
settei
~~~~~~

:copyright: (c) 2016 Spoqa, Inc.
:license: Apache License 2.0, see LICENSE for more details.

"""
import collections.abc
import pathlib
import textwrap
import typing  # noqa
import warnings

from annotation.typed import typechecked
from pytoml import load


__all__ = 'Configuration', 'ConfigWarning', 'config_property'


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

    """

    @typechecked
    def __init__(self, key: str, cls: type, docstring: str=None, **kwargs):
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

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
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
                            stacklevel=2
                        )
                    return default
                raise
        if isinstance(self.cls, typing.UnionMeta):
            cls = self.cls.__union_params__
            clsrepr = repr(cls)
        else:
            cls = self.cls
            clsrepr = '{0.__module__}.{0.__qualname__}'.format(cls)
        if not isinstance(value, cls):
            raise TypeError(
                '{0} configuration must be {1}, not {2!r}'.format(
                    self.key, clsrepr, value
                )
            )
        return value

    @property
    def docstring(self):
        """(:class:`str`) The propertly indented :attr:`__doc__` string."""
        return textwrap.dedent(self.__doc__).rstrip()

    def __repr__(self):
        return '{0.__module__}.{0.__qualname__}({1!r})'.format(
            type(self), self.key
        )


class ConfigWarning(RuntimeWarning):
    """Warning category which raised when a default configuration is used
    instead due to missing required configuration.

    """


class Configuration(collections.abc.Mapping):
    """Application instance with its settings e.g. database.  It implements
    read-only :class:`~collections.abc.Mapping` protocol as well, so you
    can treat it as a dictionary of string keys.

    """
    @classmethod
    def from_file(cls, file):
        """Load settings from the given ``file`` and instantiate an
        :class:`Configuration` instance from that.

        :param file: the file object that contains TOML settings
        :return: an instantiated configuration
        :rtype: :class:`Configuration`

        """
        return cls(load(file))

    @classmethod
    @typechecked
    def from_path(cls, path: pathlib.Path):
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
    def __init__(self, config: collections.abc.Mapping={}, **kwargs):
        self.config = dict(config, **kwargs)

    def __len__(self):
        return len(self.config)

    def __iter__(self) -> collections.abc.Iterator:
        return iter(self.config)

    def __getitem__(self, key: str):
        if isinstance(key, str):
            return self.config[key]
        raise KeyError(key)
