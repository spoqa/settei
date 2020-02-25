import uuid

from pytest import mark
from typeguard import typechecked

from settei.parse_env import parse_bool, parse_float, parse_int, parse_uuid


@mark.parametrize('v, result', [
    ('y', True),
    ('Y', True),
    ('yes', True),
    ('true', True),
    ('t', True),
    ('True', True),
    ('1', True),
    ('n', False),
    ('foobar', False),
    ('0', False),
    ('f', False),
    ('false', False),
])
@typechecked
def test_parse_bool(v: str, result: bool):
    assert parse_bool(v) == result


def test_parse_float():
    assert parse_float('3.14') == float(3.14)


def test_parse_int():
    assert parse_int('1') == 1


def test_parse_uuid():
    expected = uuid.UUID('e05bf482-c18e-4e91-b079-45bbbd5cc03c')
    assert parse_uuid('e05bf482-c18e-4e91-b079-45bbbd5cc03c') == expected
