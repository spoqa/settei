import pathlib
import typing  # noqa
import warnings

from pytest import mark, raises

from settei.base import (ConfigKeyError, ConfigTypeError,
                         Configuration, ConfigValueError, ConfigWarning,
                         config_object_property, config_property,
                         get_union_types)


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


class TestAppConfigObject(Configuration):
    no_default = config_object_property('sample.a', SampleInterface)
    with_default = config_object_property('sample.b', SampleInterface,
                                          default=Impl('default'))


def test_config_object_property():
    c = TestAppConfigObject(sample={
        'a': {
            'class': __name__ + ':Impl',
            '*': ['a', 'b', 'c'],
            'd': 4,
            'e': 5,
        },
    })
    v = c.no_default
    assert isinstance(v, Impl)
    assert v.args == ('a', 'b', 'c')
    assert v.kwargs == {'d': 4, 'e': 5}


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
