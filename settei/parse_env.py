""":mod:`settei.parse_env` --- Utility function to parse an environment vars.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.5.6

"""
import uuid

from typeguard import typechecked

__all__ = 'parse_bool', 'parse_float', 'parse_int', 'parse_uuid'


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
