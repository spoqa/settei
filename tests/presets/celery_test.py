from .logging_test import test_configure_logging as configure_test
from settei.presets.celery import WorkerConfiguration


def test_worker_config():
    conf = WorkerConfiguration({
        'worker': {
            'broker_url': 'redis://',
            'celery_result_backend': 'redis://',
        },
    })
    assert (conf.worker_config['BROKER_URL'] ==
            conf.worker_broker_url ==
            'redis://')
    assert (conf.worker_config['CELERY_RESULT_BACKEND'] ==
            conf.worker_result_backend ==
            'redis://')


def test_workeron_loaded():
    conf = WorkerConfiguration({
        'worker': {
            'on_loaded': "assert app(self) == 'ok'",
        },
    })
    log = []
    conf.on_worker_loaded(lambda self: log.append(self) or 'ok')
    assert log == [conf]


def test_configure_logging():
    configure_test('settei.workertest.', WorkerConfiguration)
