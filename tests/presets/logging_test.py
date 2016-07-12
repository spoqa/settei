import logging

from settei.presets.logging import LoggingConfiguration


class TestHandler(logging.Handler):

    records = []

    def emit(self, record):
        self.records.append(self.format(record))


def test_configure_logging(prefix: str='settei.tests.',
                           conf_cls: type=LoggingConfiguration):
    TestHandler.records = []
    a = logging.getLogger(prefix + 'a')
    b = logging.getLogger(prefix + 'b')
    c = logging.getLogger(prefix + 'c')

    def log():
        for level in 'debug', 'info', 'warn', 'error':
            for v, l in [('a', a), ('b', b), ('c', c)]:
                getattr(l, level)('%s %s', level, v)
    assert not a.hasHandlers()
    assert not b.hasHandlers()
    assert not c.hasHandlers()
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
    assert not a.hasHandlers()
    assert not b.hasHandlers()
    assert not c.hasHandlers()
    log()
    assert not TestHandler.records
    conf.configure_logging()
    assert a.hasHandlers()
    assert b.hasHandlers()
    assert c.hasHandlers()
    log()
    assert TestHandler.records == [
        'warn a',
        'warn b',
        'warn c',
        'error a',
        'error b',
        'error c',
    ]
