""":mod:`settei.presets.flask` --- Preset for Flask apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
import typing

from tsukkomi.typed import typechecked
from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import cached_property

from ..base import config_property
from .logging import LoggingConfiguration

__all__ = 'WebConfiguration',


class WebConfiguration(LoggingConfiguration):

    web_debug = config_property(
        'web.debug', bool,
        """Whether to enable debug mode.  On debug mode the server will reload
        itself on code changes, and provide a helpful debugger when things go
        wrong.

        """,
        default=False
    )

    @cached_property
    def web_config(self) -> typing.Mapping[str, object]:
        """(:class:`typing.Mapping`) The configuration maping for
        web that will go to :attr:`flask.Flask.config <Flask.config>`.

        """
        web_config = self.config.get('web', {})
        if not isinstance(web_config, collections.abc.Mapping):
            web_config = {}
        return ImmutableDict((k.upper(), v) for k, v in web_config.items())

    @typechecked
    def on_web_loaded(self, app: typing.Callable):
        """Be invoked when a WSGI app is ready.

        :param app: a ready wsgi/flask app
        :type app: :class:`flask.Flask`, :class:`typing.Callable`

        """
        self.configure_logging()
        exec(self.config.get('web', {}).get('on_loaded', ''),
             None,
             {'self': self, 'app': app})
