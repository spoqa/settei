from flask import Flask
from .logging_test import test_configure_logging as configure_test
from settei.presets.flask import WebConfiguration


def test_web_debug():
    conf = WebConfiguration({
        'web': {'debug': True}
    })
    assert conf.web_debug
    conf2 = WebConfiguration({
        'web': {'debug': False}
    })
    assert not conf2.web_debug
    conf3 = WebConfiguration({'web': {}})
    assert not conf3.web_debug
    conf4 = WebConfiguration({})
    assert not conf4.web_debug


def test_web_config():
    conf = WebConfiguration({
        'web': {
            'debug': True,
            'testing': True,
            'secret_key': 'asdf',
        },
    })
    assert conf.web_config['DEBUG']
    assert conf.web_config['TESTING']
    assert conf.web_config['SECRET_KEY'] == 'asdf'


def test_web_on_loaded():
    conf = WebConfiguration({
        'web': {
            'on_loaded': "assert app.name == '{}'\n"
                         "app.name = 'ok'".format(__name__),
        },
    })
    app = Flask(__name__)
    conf.on_web_loaded(app)
    assert app.name == 'ok'


def sample_hook(conf: WebConfiguration, app: Flask):
    assert app.name == __name__
    app.name = 'ok'


def test_web_on_loaded_hooks_list():
    conf = WebConfiguration({
        'web': {
            'on_loaded': [__name__ + ':' + sample_hook.__name__],
        },
    })
    app = Flask(__name__)
    conf.on_web_loaded(app)
    assert app.name == 'ok'


def test_web_on_loaded_with_callable():
    conf = WebConfiguration({
        'web': {
            'on_loaded': "assert app(self) == 'ok'",
        },
    })
    log = []
    conf.on_web_loaded(lambda self: log.append(self) or 'ok')
    assert log == [conf]


def test_configure_logging():
    configure_test('settei.webtest.', WebConfiguration)
