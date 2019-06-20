""":mod:`settei.presets.flask` --- Preset for Flask apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.2.0

"""
import collections.abc
import typing

from typeguard import typechecked
from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import cached_property

from ..base import config_property
from ..utils import import_hook
from .logging import LoggingConfiguration

__all__ = 'WebConfiguration',


class WebConfiguration(LoggingConfiguration):
    """Settei configuration for the `Flask`_. For more information, See the
    example below:

    .. code-block:: python

       config = WebConfiguration.from_path('config.toml')
       app = Flask(__name__)
       app.config.update(config.web_config)

       @app.before_first_request
       def before_first_request():
           config.on_web_loaded(app)

       app.run()

    .. _Flask: http://flask.pocoo.org/

    """

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
    def on_web_loaded(self, app: typing.Callable[..., typing.Any]):
        """Trigger the ``web.on_loaded`` hooks.
        You should invoke this function when the WSGI app is ready
        with the WSGI app as argument.
        You may want to use :attr:`flask.Flask.before_first_request`.

        ``web.on_loaded`` hook can be a Python code or list of module path.

        When ``web.on_loaded`` is a single string, it will be interpreted as
        Python code.
        The configuration and the WSGI app is injected as ``self`` and ``app``
        each:

        .. code-block:: toml

           [web]
           on_loaded = \"""
           print('Hello, world!')
           print('self is configuration!: {}'.format(self))
           print('app is flask app!: {}'.format(app))
           \"""


        When ``web.on_loaded`` is a list of string, it will be interpreted as
        module paths:

        .. code-block:: toml

           [web]
           on_loaded = [
               "utils.hooks:sample_hook",
               "src.main:print_hello_world",
           ]

        The hooks must receive two arguments, :class:`Configuration` and
        :class:`flask.Flask`:

        .. code-block:: python

           def sample_hook(conf: Configuration, app: Flask):
               print('Hello, world!')
               print('conf is configuration!: {}'.format(conf))
               print('app is flask app!: {}'.format(app))

        :param app: a ready wsgi/flask app
        :type app: :class:`flask.Flask`, :class:`typing.Callable`

        .. versionchanged:: 0.5.2
           Hooks list added

        .. versionchanged:: 0.5.3
           Change the ``app`` argument type to :class:`typing.Callable`

        """
        self.configure_logging()

        on_loaded = self.config.get('web', {}).get('on_loaded', [])

        if isinstance(on_loaded, (list, tuple)):
            for hook_path in on_loaded:
                func = import_hook(hook_path)
                func(self, app)
        else:
            exec(
                on_loaded,
                None,
                {
                    'self': self,
                    'app': app
                },
            )
