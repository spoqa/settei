""":mod:`settei.presets.celery` --- Preset for Celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
import typing

from kombu.utils import cached_property

from ..base import config_property
from .logging import LoggingConfiguration

__all__ = 'WorkerConfiguration',


class WorkerConfiguration(LoggingConfiguration):
    """The application object mixin which holds configuration for Celery."""

    worker_broker_url = config_property(
        'worker.broker_url', str,
        """The url of the broker used by Celery.  See also Celery's and
        Kombu's docs about broker urls:

        http://docs.celeryproject.org/en/latest/configuration.html#broker-url
        http://kombu.readthedocs.org/en/latest/userguide/connections.html#connection-urls

        """
    )

    worker_result_backend = config_property(
        'worker.celery_result_backend', str,
        """The backend used by Celery to store task results.  See also Celery's
        docs about result backends:

        http://docs.celeryproject.org/en/latest/configuration.html#celery-result-backend

        """
    )

    @cached_property
    def worker_config(self) -> typing.Mapping[str, object]:
        """(:class:`typing.Mapping`\ [:class:`str`, :class:`object`])
        The configuration maping for worker that will go to :attr:`Celery.conf
        <celery.Celery.conf>`.

        """
        celery_config = self.config.get('worker', {})
        if not isinstance(celery_config, collections.abc.Mapping):
            celery_config = {}
        celery_config.update(
            BROKER_URL=self.worker_broker_url,
            CELERY_RESULT_BACKEND=self.worker_result_backend
        )
        return {k.upper(): v for k, v in celery_config.items()}

    def on_worker_loaded(self, app):
        """Be invoked when a Celery app is ready.

        :param app: a ready celery app
        :type app: :class:`celery.Celery`

        """
        self.configure_logging()
        exec(self.config.get('worker', {}).get('on_loaded', ''),
             None,
             {'self': self, 'app': app})
