""":mod:`settei.parse_env` --- Utility function to parse an environment vars.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.5.6

"""
import collections
import os
import typing
import uuid

from typeguard import typechecked

__all__ = 'EnvReader', 'parse_bool', 'parse_float', 'parse_int', 'parse_uuid'


@typechecked
def parse_bool(v: str) -> bool:
    """Parse boolean type. It returns ``True``
    when ``v`` is in one of the following values (``'y'``, ``'yes'``, ``'t'``,
    ``'true'``, `'1'`).

    .. note::

       Since it tries to parse a value into lowercase, ``'Yes'``, ``'True'``,
       ``'Y'`` represent ``True`` as well. (even ``'yEs'``, ``'YeS'`` ...)

    :param v: An environment variable to parse.
    :type v: :class:`str`
    :return: A boolean type value
    :rtype: :class:`bool`

    .. versionadded:: 0.5.6

    """
    return v.lower() in ('y', 'yes', 't', 'true', '1')


@typechecked
def parse_float(v: str) -> float:
    """Parse float type.

    :param v: An environment variable to parse.
    :type v: :class:`str`
    :return: A float type value
    :rtype: :class:`float`

    .. versionadded:: 0.5.6

    """
    return float(v)


@typechecked
def parse_int(v: str) -> int:
    """Parse int type.

    :param v: An environment variable to parse.
    :type v: :class:`str`
    :return: A int type value
    :rtype: :class:`int`

    .. versionadded:: 0.5.6

    """
    return int(v)


@typechecked
def parse_uuid(v: str) -> uuid.UUID:
    """Parse UUID type.

    :param v: An environment variable to parse.
    :type v: :class:`str`
    :return: A UUID type value
    :rtype: :class:`uuid.UUID`

    .. versionadded:: 0.5.6

    """
    return uuid.UUID(v)


class EnvReader(collections.abc.Mapping):
    DELIMITER = '__'
    ASTERISK_CHAR = 'ASTERISK'
    LIST_CHAR = 'SETTEIENVLIST'

    def __init__(
        self, conf: typing.Mapping[str, object] = {},
        froms: typing.Optional[str] = None, **kwargs
    ):
        self.conf = dict(conf, **kwargs)
        self.froms = froms

    def __iter__(self):
        return self.conf.__iter__()

    def __len__(self):
        return self.conf.__len__()

    def __getitem__(self, key: str) -> typing.Any:
        result = None
        try:
            result = self.conf[key]
        except KeyError:
            os_key = upper_key = key.upper()
            if self.froms is not None:
                os_key = self.DELIMITER.join([self.froms, upper_key])
            if os_key in os.environ:
                result = os.environ[os_key]
            else:
                lookup_key = '{}{}'.format(os_key, self.DELIMITER)
                env_keys = [
                    k
                    for k in os.environ
                    if k.startswith(lookup_key)
                ]
                if env_keys and any(
                    len(key.split(self.DELIMITER)) >= 2
                    for key in env_keys
                ):
                    results = self._transform_asterisk_and_list(
                        upper_key, env_keys
                    )
                    if not results:
                        return EnvReader(froms=os_key)
                    return results
        if not result:
            raise KeyError(key)
        return result

    def _transform_asterisk_and_list(
        self, upper_key: str, env_keys: typing.List[str],
    ) -> typing.Union[typing.List, typing.Tuple]:
        list_results = []
        asterisk_results = []
        for env_key in env_keys:
            keys = env_key.split(self.DELIMITER)
            key_index = keys.index(upper_key)

            result = self._value_from_env(keys[key_index:], env_key, True)
            if keys[key_index + 1] == self.LIST_CHAR:
                list_results.append((keys[key_index + 2], result))
            elif keys[key_index + 1] == self.ASTERISK_CHAR:
                asterisk_results.append((keys[key_index + 2], result))
        return self._convert_sorted_results(list_results) or \
            tuple(self._convert_sorted_results(asterisk_results))

    def _convert_sorted_results(
        self, results: typing.List[typing.Tuple[int, typing.Any]],
    ) -> typing.List[typing.Any]:
        return [r[1] for r in sorted(results, key=lambda x: x[0])]

    def _value_from_env(
        self, keys: typing.List[str], env_key: str, unpacked: bool = False,
    ) -> typing.Union[str, typing.List, typing.Tuple]:
        asterisk_indexes = [
            i for i, key in enumerate(keys)
            if key == self.ASTERISK_CHAR
        ]
        list_indexes = [
            i for i, key in enumerate(keys)
            if key == self.LIST_CHAR
        ]
        if not (asterisk_indexes or list_indexes):
            return os.environ[env_key]

        result = self._value_from_env(keys[1:], env_key)
        if not unpacked and keys[1] == self.ASTERISK_CHAR:
            return (result,)
        elif not unpacked and keys[1] == self.LIST_CHAR:
            return [result]
        return result

    def __repr__(self) -> str:
        return '{0.__module__}.{0.__qualname__}({1!r})'.format(
            type(self), self.conf
        )
