import logging

from settei.presets.logging import LoggingConfiguration


class TestHandler(logging.Handler):

    records = []

    def emit(self, record):
        self.records.append(self.format(record))


def has_handlers(logger: logging.Logger) -> bool:
    while logger is not None:
        for h in logger.handlers:
            if type(h).__module__.startswith(('pytest.', '_pytest')):
                continue
            return True
        logger = logger.parent
    return False


def test_configure_logging(prefix: str = 'settei.tests.',
                           conf_cls: type = LoggingConfiguration):
    TestHandler.records = []
    a = logging.getLogger(prefix + 'a')
    b = logging.getLogger(prefix + 'b')
    c = logging.getLogger(prefix + 'c')

    def log():
        for level in 'debug', 'info', 'warning', 'error':
            for v, l in [('a', a), ('b', b), ('c', c)]:
                getattr(l, level)('%s %s', level, v)
    assert not has_handlers(a)
    assert not has_handlers(b)
    assert not has_handlers(c)
    log()
    assert not TestHandler.records
    handler_typename = '{0.__module__}.{0.__qualname__}'.format(TestHandler)
    conf = conf_cls({
        'logging': {
            'version': 1,
            'loggers': {
                prefix + 'a': {'handlers': ['testhandler']},
                prefix + 'b': {'handlers': ['testhandler']},
                prefix + 'c': {'handlers': ['testhandler']},
            },
            'handlers': {
                'testhandler': {
                    'class': handler_typename,
                    'level': 'WARNING',
                },
            },
        },
    })
    assert not has_handlers(a)
    assert not has_handlers(b)
    assert not has_handlers(c)
    log()
    assert not TestHandler.records
    conf.configure_logging()
    assert has_handlers(a)
    assert has_handlers(b)
    assert has_handlers(c)
    log()
    assert TestHandler.records == [
        'warning a',
        'warning b',
        'warning c',
        'error a',
        'error b',
        'error c',
    ]
