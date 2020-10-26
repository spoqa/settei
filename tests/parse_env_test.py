import os
import uuid

from pytest import mark, raises
from typeguard import typechecked

from .utils import os_environ
from settei.parse_env import (
    EnvReader, parse_bool, parse_float, parse_int, parse_uuid,
)


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


def test_env_reader():
    d = EnvReader({'a': 1})
    # get key properly
    assert d['a'] == 1
    # get dict first instead of env
    with os_environ({'A': '3'}):
        os.environ['A'] = '3'
        assert d['a'] == 1
    # raises KeyError
    with raises(KeyError):
        d['z']


def test_env_reader_depth():
    # get os env properly
    d = EnvReader()
    with os_environ({'C': '2'}):
        os.environ['C'] = '2'
        assert d['c'] == '2'
    with os_environ({'A__C': '2'}):
        assert d['a']['c'] == '2'
    with os_environ({'A__B': '3', 'A__C__D': '2'}):
        assert d['a']['b'] == '3'
        assert d['a']['c']['d'] == '2'
    with os_environ({'D__E__F': '3'}):
        assert d['d']['e']['f'] == '3'
    with os_environ({'D__E__F__G': '4'}):
        assert d['d']['e']['f']['g'] == '4'
    with os_environ({'A__B__C__D__E': '5'}):
        assert d['a']['b']['c']['d']['e'] == '5'


def test_env_reader_setteienvlist():
    # get os env properly (setteienvlist)
    d = EnvReader()
    with os_environ(
        {
            'A__SETTEIENVLIST__0': 'test1',
            'A__SETTEIENVLIST__2': 'test3',
            'A__SETTEIENVLIST__1': 'test2',
            'A__SETTEIENVLIST__4': 'test5',
            'A__SETTEIENVLIST__3': 'test4',
        }
    ):
        assert d['a'] == ['test1', 'test2', 'test3', 'test4', 'test5']
    with os_environ(
        {
            'A__B__SETTEIENVLIST__0': 'test1',
            'A__B__SETTEIENVLIST__1': 'test2',
        }
    ):
        assert d['a']['b'] == ['test1', 'test2']
    with os_environ(
        {
            'A__B__C__SETTEIENVLIST__0': 'test1',
            'A__B__C__SETTEIENVLIST__1': 'test2',
        }
    ):
        assert d['a']['b']['c'] == ['test1', 'test2']
    with os_environ(
        {
            'A__SETTEIENVLIST__0__SETTEIENVLIST__0': 'test1',
            'A__SETTEIENVLIST__1': 'test2',
        }
    ):
        assert d['a'] == [['test1'], 'test2']
    # get os env only (priority test)
    with os_environ(
        {
            'A__B': 'test',
            'A__B__SETTEIENVLIST__0': 'test1',
            'A__B__SETTEIENVLIST__1': 'test2',
        }
    ):
        assert d['a']['b'] == 'test'


def test_env_reader_asterisk():
    # get os env properly (asterisk)
    d = EnvReader()
    with os_environ(
        {
            'A__ASTERISK__0': 'arg1',
            'A__ASTERISK__1': 'arg2',
        }
    ):
        assert d['a'] == ('arg1', 'arg2')
    with os_environ(
        {
            'A__ASTERISK__1': 'arg2',
            'A__ASTERISK__0': 'arg1',
        }
    ):
        assert d['a'] == ('arg1', 'arg2')


def test_env_reader_asterisk_setteienvlist():
    # get os env properly (asterisk and setteienvlist)
    d = EnvReader()
    with os_environ(
        {
            'A__ASTERISK__0__SETTEIENVLIST__0': 'arg1',
            'A__ASTERISK__1': 'arg2',
        }
    ):
        assert d['a'] == (['arg1'], 'arg2')

    with os_environ(
        {
            'A__ASTERISK__0__SETTEIENVLIST__0__SETTEIENVLIST__0': 'arg1',
            'A__ASTERISK__1': 'arg2',
        }
    ):
        assert d['a'] == ([['arg1']], 'arg2')

    with os_environ(
        {
            'A__ASTERISK__0__ASTERISK__0__SETTEIENVLIST__0': 'arg1',
            'A__ASTERISK__1': 'arg2',
        }
    ):
        assert d['a'] == ((['arg1'],), 'arg2')
