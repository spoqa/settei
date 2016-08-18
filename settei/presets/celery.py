""":mod:`settei.presets.celery` --- Preset for Celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
import datetime
import re
import typing
import warnings

from celery.schedules import crontab
from celery.utils.imports import symbol_by_name
from kombu.utils import cached_property

from ..base import ConfigWarning, config_property
from .logging import LoggingConfiguration

__all__ = 'SCHEDULE_EXPR_PATTERN', 'WorkerConfiguration',


SCHEDULE_EXPR_PATTERN = re.compile(r'''
    ^
    (?:
        (?P<module_path>
            (?:    [^\d\W] \w* )
            (?: \. [^\d\W] \w* )*
        )
        :
    )?
    (?P<call>
        (?P<function> [^\d\W] \w* )
        \( .*? \)
    )
    $
''', re.VERBOSE | re.UNICODE)


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
    def worker_schedule(self) -> typing.Mapping[str,
                                                typing.Mapping[str, object]]:
        """(:class:`typing.Mapping`\ [:class:`str`,
        :class:`typing.Mapping`\ [:class:`str`, :class:`object`]])
        The schedule table for Celery Beat, scheduler for periodic tasks.

        There's some preprocessing before reading configuration.
        Since TOML doesn't have custom types, you can't represent
        :class:`~datetime.timedelta` or :class:`~celery.schedules.crontab`
        values from the configuration file.  To workaround the problem,
        it evaluates strings like ``'f()'`` pattern if they are appeared
        in a ``schedule`` field.

        For example, if the following configuration is present:

        .. code-block:: toml

           [worker.celerybeat_schedule.add-every-30-seconds]
           task = "tasks.add"
           schedule = "timedelta(seconds=30)"  # string to be evaluated
           args = [16, 16]

        it becomes translated to:

        .. code-block:: python

           CELERYBEAT_SCHEDULE = {
               'add-every-30-seconds': {
                   'task': 'tasks.add',
                   'schedule': datetime.timedelta(seconds=30),  # evaluated!
                   'args': (16, 16),
               },
           }

        Note that although :class:`~datetime.timedelta` and
        :class:`~celery.schedules.crontab` is already present in the context,
        you need to import things if other types.  It can also parse and
        evaluate the patterns like ``'module.path:func()'``.

        Also ``args`` fields are translated from array to tuple.

        See also Celery's docs about periodic tasks:

        http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html

        .. versionadded:: 0.2.1

        """
        raw_config = self.config.get('worker', {})
        try:
            table = raw_config['celerybeat_schedule']
        except KeyError:
            try:
                table = next(
                    v for k, v in raw_config.items()
                    if k.lower() == 'celerybeat_schedule'
                )
            except StopIteration:
                return {}
        base_ctx = {'timedelta': datetime.timedelta, 'crontab': crontab}
        new_table = {}
        for name, value in table.items():
            try:
                schedule = value['schedule']
            except KeyError:
                warnings.warn(
                    'the {0!r} of worker.celerybeat_schedule lacks schedule '
                    'field'.format(name),
                    ConfigWarning
                )
                new_table[name] = value
                continue
            if not isinstance(schedule, str):
                warnings.warn(
                    'the schedule field of worker.celerybeat_schedule.{0} '
                    'has to be a string'.format(name),
                    ConfigWarning
                )
                new_table[name] = value
                continue
            match = SCHEDULE_EXPR_PATTERN.match(schedule)
            if not match:
                warnings.warn(
                    'the schedule field of worker.celerybeat_schedule.{0} '
                    'is invalid format.  it has to be like "f(args)" or '
                    '"module.path:func(args)'.format(name),
                    ConfigWarning
                )
                new_table[name] = value
                continue
            ctx = base_ctx.copy()
            if match.group('module_path'):
                import_path = '{}:{}'.format(match.group('module_path'),
                                             match.group('function'))
                ctx[match.group('function')] = symbol_by_name(import_path)
            new_table[name] = dict(value,
                                   args=tuple(value.get('args', ())),
                                   schedule=eval(match.group('call'), ctx))
        return new_table

    @cached_property
    def worker_config(self) -> typing.Mapping[str, object]:
        """(:class:`typing.Mapping`\ [:class:`str`, :class:`object`])
        The configuration maping for worker that will go to :attr:`Celery.conf
        <celery.Celery.conf>`.

        """
        raw_config = self.config.get('worker', {})
        if isinstance(raw_config, collections.abc.Mapping):
            celery_config = {k.upper(): v for k, v in raw_config.items()}
        else:
            celery_config = {}
        celery_config.update(
            BROKER_URL=self.worker_broker_url,
            CELERY_RESULT_BACKEND=self.worker_result_backend,
            CELERYBEAT_SCHEDULE=self.worker_schedule
        )
        return celery_config

    def on_worker_loaded(self, app):
        """Be invoked when a Celery app is ready.

        :param app: a ready celery app
        :type app: :class:`celery.Celery`

        """
        self.configure_logging()
        exec(self.config.get('worker', {}).get('on_loaded', ''),
             None,
             {'self': self, 'app': app})
