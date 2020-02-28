import enum
import os
import pathlib
import typing  # noqa
import warnings

from pytest import mark, raises

from settei.base import (ConfigKeyError, ConfigTypeError,
                         Configuration, ConfigValueError, ConfigWarning,
                         config_object_property, config_property,
                         get_union_types)


class Enum1(enum.Enum):
    apple = 'apple'
    banana = 'banana'
    cherry = 'cherry'


class Enum2(enum.Enum):
    apple = 'apple'
    bear = 'bear'
    candy = 'candy'


def test_get_union_types():
    assert get_union_types(typing.Union[int, str]) == (int, str)
    assert get_union_types(typing.Union[bool, list, set]) == (bool, list, set)
    assert get_union_types(str) is None
    assert get_union_types('asdf') is None


def test_package_level_api_compatibility():
    import settei
    assert settei.Configuration is Configuration
    assert settei.ConfigWarning is ConfigWarning
    assert settei.config_property is config_property


class TestConfig(dict):
    depth1_required = config_property('key', int)
    depth1_optional = config_property('key', int, default='')
    depth1_warn = config_property('key', int, default='', default_warning=True)
    depth1_default_func = config_property(
        'key', int,
        default_func=lambda self: self.depth1_optional
    )
    depth1_default_func_warn = config_property(
        'key', int,
        default_func=lambda self: self.depth1_optional,
        default_warning=True
    )
    depth2_required = config_property('section.key', str)
    depth2_optional = config_property('section.key', str, default=None)
    depth2_warn = config_property('section.key', str,
                                  default=None, default_warning=True)
    union = config_property('union', typing.Union[int, str])


class EnumTestConfig(dict):
    enum = config_property('enum', Enum1, default=Enum1.apple)
    enum_union = config_property('enum_union', typing.Union[Enum1, Enum2, str])


class TestAppConfig(Configuration):
    database_url = config_property(
        'database.url', str,
        default='sqlite:///test_app.db', default_warning=True
    )


@mark.parametrize('union_value', [123, 'string'])
def test_config_property(union_value: typing.Union[int, str]):
    c = TestConfig(key=123, section={'key': 'val'}, union=union_value)
    assert c.depth1_required == 123
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_optional == 123
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_warn == 123
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_default_func == 123
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_default_func_warn == 123
        assert len(w) == 0
    assert c.depth2_required == 'val'
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_optional == 'val'
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_warn == 'val'
        assert len(w) == 0
    assert c.union == union_value


def test_enum_config_property():
    c1 = EnumTestConfig(enum='apple', enum_union='banana')
    c2 = EnumTestConfig(enum='banana', enum_union='candy')
    c3 = EnumTestConfig(enum='dragonfruit', enum_union='apple')
    c4 = EnumTestConfig(enum='cherry', enum_union='foo')
    assert c1.enum == Enum1.apple
    assert c2.enum == Enum1.banana
    assert c1.enum_union == Enum1.banana
    assert c2.enum_union == Enum2.candy
    with raises(ConfigTypeError) as ex:
        c3.enum
    assert ex.value.args[0] == 'Invalid value dragonfruit in <enum \'Enum1\'>. Candidates are: apple, banana, cherry'  # noqa
    with raises(ConfigTypeError) as ex:
        c3.enum_union
    assert ex.value.args[0] == 'Ambiguous enum type for value apple: <Enum1.apple: \'apple\'>, <Enum2.apple: \'apple\'>'  # noqa
    assert c4.enum_union == 'foo'


def test_config_property_absence():
    c = TestConfig()
    with raises(ConfigKeyError):
        c.depth1_required
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_optional == ''
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_warn == ''
        assert len(w) == 1
        assert issubclass(w[-1].category, ConfigWarning)
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_default_func == ''
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth1_default_func_warn == ''
        assert len(w) == 1
        assert issubclass(w[-1].category, ConfigWarning)
    with raises(ConfigKeyError):
        c.depth2_required
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_optional is None
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_warn is None
        assert len(w) == 1
        assert issubclass(w[-1].category, ConfigWarning)
    with raises(ConfigKeyError):
        c.union


def test_config_property_absence_2nd_depth():
    c = TestConfig(section={})
    with raises(ConfigKeyError):
        c.depth2_required
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_optional is None
        assert len(w) == 0
    with warnings.catch_warnings(record=True) as w:
        assert c.depth2_warn is None
        assert len(w) == 1
        assert issubclass(w[-1].category, ConfigWarning)


def test_config_property_type_error():
    c = TestConfig(key='not an integer')
    with raises(ConfigTypeError):
        c.depth1_required
    c2 = TestConfig()
    assert isinstance(c2.depth1_optional, str), \
        'default should be possible to bypass typecheck'
    assert isinstance(c2.depth1_default_func, str), \
        'default_func should be possible to bypass typecheck'


class SampleInterface:
    pass


class Impl(SampleInterface):

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        args = ', '.join(repr(arg) for arg in self.args)
        kwargs = ', '.join('{0}={1!r}'.format(k, v)
                           for k, v in self.kwargs.items())
        if kwargs:
            args += (', ' if args else '') + kwargs
        return '{0.__module__}.{0.__name__}({1})'.format(type(self), args)


class TestAppConfigObject(Configuration):
    no_default = config_object_property('sample.a', SampleInterface)
    with_default = config_object_property('sample.b', SampleInterface,
                                          default=Impl('default'))
    recursive = config_object_property('sample.c', SampleInterface,
                                       recurse=True)
    cached = config_object_property('sample.a', SampleInterface, cached=True)
    cached_with_default = config_object_property('sample.b', SampleInterface,
                                                 default=Impl('default'),
                                                 cached=True)


def test_config_object_property():
    c = TestAppConfigObject(sample={
        'a': {
            'class': __name__ + ':Impl',
            '*': ['a', 'b', 'c'],
            'd': 4,
            'e': 5,
            'f': {
                'class': __name__ + ':Impl',
                'nested': True,
                'recursive': {
                    'class': __name__ + ':Impl',
                    'nested': True,
                }
            },
        },
    })
    v = c.no_default
    assert isinstance(v, Impl)
    assert v.args == ('a', 'b', 'c')
    assert v.kwargs == {
        'd': 4, 'e': 5,
        'f': {
            'class': __name__ + ':Impl',
            'nested': True,
            'recursive': {
                'class': __name__ + ':Impl',
                'nested': True,
            }
        },
    }
    assert c.no_default is not c.no_default
    vv = c.with_default
    assert isinstance(vv, Impl)
    assert vv.args == ('default',)
    assert vv.kwargs == {}


def test_config_object_property_recurse():
    c = TestAppConfigObject(sample={
        'a': {'class': __name__ + ':Impl'},
        'c': {
            'class': __name__ + ':Impl',
            '*': ['a', 'b', 'c'],
            'd': 4,
            'e': 5,
            'f': {
                'class': __name__ + ':Impl',
                'nested': True,
                'recursive': {
                    'class': __name__ + ':Impl',
                    'nested': True,
                }
            },
        },
    })
    v = c.recursive
    assert isinstance(v, Impl)
    assert v.args == ('a', 'b', 'c')
    assert frozenset(v.kwargs) == frozenset({'d', 'e', 'f'})
    assert v.kwargs['d'] == 4
    assert v.kwargs['e'] == 5
    f = v.kwargs['f']
    assert isinstance(f, Impl)
    assert f.args == ()
    assert frozenset(f.kwargs) == frozenset({'nested', 'recursive'})
    assert f.kwargs['nested'] is True
    r = f.kwargs['recursive']
    assert isinstance(r, Impl)
    assert r.args == ()
    assert r.kwargs == {'nested': True}


def test_config_object_property_not_dict_error():
    c = TestAppConfigObject(sample={'a': 'Not dict'})
    with raises(ConfigTypeError):
        c.no_default


def test_config_object_property_no_class_field_error():
    c = TestAppConfigObject(sample={'a': {}})
    with raises(ConfigValueError):
        c.no_default


def test_config_object_property_invalid_class_field_error():
    invalid_syntax = TestAppConfigObject(sample={
        'a': {'class': 'invalid.import.path'},
    })
    with raises(ConfigValueError):
        invalid_syntax.no_default
    invalid_type = TestAppConfigObject(sample={
        'a': {'class': 'os.path:supports_unicode_filenames'},
    })
    with raises(ConfigValueError):
        invalid_type.no_default


def test_config_object_property_invalid_args_error():
    non_list = TestAppConfigObject(sample={
        'a': {
            'class': __name__ + ':Impl',
            '*': 123,  # must be a list, but it's an integer, which is wrong
        },
    })
    with raises(ConfigValueError):
        non_list.no_default
    string = TestAppConfigObject(sample={
        'a': {
            'class': __name__ + ':Impl',
            '*': 'abc',  # string is not valid either
        },
    })
    with raises(ConfigValueError):
        string.no_default


def test_app_from_file(tmpdir):
    path = tmpdir.join('cfg.toml')
    path.write('''
    [database]
    url = "sqlite:///a.db"
    ''')
    with path.open() as f:
        cfg = TestAppConfig.from_file(f)
    assert cfg.database_url == 'sqlite:///a.db'


def test_app_from_path(tmpdir):
    path = tmpdir.join('cfg.toml')
    path.write('''
    [database]
    url = "sqlite:///b.db"
    ''')
    cfg = TestAppConfig.from_path(pathlib.Path(path.strpath))
    assert cfg.database_url == 'sqlite:///b.db'


def test_config_object_property_cached():
    c = TestAppConfigObject(sample={
        'a': {
            'class': __name__ + ':Impl',
            '*': ['a', 'b', 'c'],
            'd': 4,
            'e': 5,
        },
    })
    assert c.cached is c.cached
    assert isinstance(c.cached, Impl)
    assert c.cached.args == ('a', 'b', 'c')
    assert c.cached.kwargs == {'d': 4, 'e': 5}
    assert isinstance(c.cached_with_default, Impl)
    assert c.cached_with_default.args == ('default',)
    assert c.cached_with_default.kwargs == {}


def parse_foo(d: typing.Mapping[str, str]):
    r = d.copy()
    r.update({
        '*': [int(x) for x in d['*'][0]],
        'foo': float(d['foo']),
    })
    return r


class TestEnvAppConfig(dict):

    env_lookup = config_property('foo.bar', str, lookup_env=True)
    env_with_name = config_property('foo.baz', str, lookup_env=True,
                                    env_name='LOREM_IPSUM')
    env_false = config_property('foo.qux', str, lookup_env=False)
    env_error = config_property('foo.quux', str, lookup_env=True)
    given_first = config_property('foo.quuz', str, lookup_env=True)
    parse = config_property('foo.parse', bool,
                            lookup_env=True, parse_env=lambda x: x == 'True')
    empty_text = config_property('foo.empty', str, lookup_env=True)
    env_object = config_object_property('foo.obj', SampleInterface)
    recursiveobj = config_object_property('foo.recurse', SampleInterface,
                                          recurse=True)

    parse_object = config_object_property(
        'foo.parse',
        SampleInterface,
        parse=parse_foo
    )


def test_config_property_lookup_env():
    os.environ['FOO__BAR'] = 'hi'
    os.environ['LOREM_IPSUM'] = 'gg'
    os.environ['FOO__QUX'] = 'qux'
    os.environ['FOO__QUUZ'] = 'quuz'
    os.environ['FOO__EMPTY'] = ''
    c = TestEnvAppConfig(foo={'quuz': 'gl'})
    assert c.env_lookup == 'hi', \
        'Get env var when given configuration is missing.'
    assert c.env_with_name == 'gg', \
        'Get env var which one has diffrent name.'
    assert c.given_first == 'gl', \
        'Get given configuration even if env var is exist.'
    # no look up env, no configration = Error
    with raises(ConfigKeyError):
        c.env_false
    # no env, no configration = Error
    with raises(ConfigKeyError):
        c.env_error
    # should allow empty text
    assert c.empty_text == ''


def test_config_property_convert_func():
    os.environ['FOO__PARSE'] = 'True'
    c = TestEnvAppConfig(foo={})
    assert c.parse
    os.environ['FOO__PARSE'] = 'False'
    assert not c.parse


def test_config_object_property_env():
    os.environ['FOO__OBJ__CLASS'] = __name__ + ':Impl'
    os.environ['FOO__OBJ__FOO'] = 'foo'
    os.environ['FOO__OBJ__BAR'] = 'bar'
    c = TestEnvAppConfig(foo={})
    assert c.env_object.kwargs == {
        'foo': 'foo',
        'bar': 'bar',
    }


def test_config_object_property_env_recurse():
    os.environ['FOO__RECURSE__CLASS'] = __name__ + ':Impl'
    os.environ['FOO__RECURSE__*__0'] = 'lorem'
    os.environ['FOO__RECURSE__F__CLASS'] = __name__ + ':Impl'
    os.environ['FOO__RECURSE__F__NESTED'] = 'true'
    os.environ['FOO__RECURSE__F__RECURSIVE__CLASS'] = __name__ + ':Impl'
    os.environ['FOO__RECURSE__F__RECURSIVE__NESTED'] = 'true'
    os.environ['FOO__RECURSE__F__RECURSIVE__*__0'] = 'hi'
    os.environ['FOO__RECURSE__F__RECURSIVE__*__1'] = 'mi'
    os.environ['FOO__RECURSE__F__RECURSIVE__*__2'] = 'me'
    c = TestEnvAppConfig(foo={})
    v = c.recursiveobj
    assert isinstance(v, Impl)
    assert frozenset(v.kwargs) == frozenset({'f'})
    assert v.args == ('lorem', )
    f = v.kwargs['f']
    assert isinstance(f, Impl)
    assert f.args == ()
    assert frozenset(f.kwargs) == frozenset({'nested', 'recursive'})
    assert f.kwargs['nested'] == 'true'
    r = f.kwargs['recursive']
    assert isinstance(r, Impl)
    assert r.args == ('hi', 'mi', 'me')
    assert r.kwargs == {'nested': 'true'}


def test_config_object_property_env_parse():
    os.environ['FOO__PARSE__CLASS'] = __name__ + ':Impl'
    os.environ['FOO__PARSE__*__0'] = '1'
    os.environ['FOO__PARSE__FOO'] = '3.14'
    c = TestEnvAppConfig(foo={})
    assert c.parse_object.args == (1, )
    assert c.parse_object.kwargs == {'foo': 3.14}
