""":mod:`settei.presets.logging` --- Preset for :mod:`logging` configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.2.0

Preset for apps holding :mod:`logging` configuration.  Logging can be
configured through TOML file e.g.:

.. code-block:: toml

   [logging]
   version = 1

   [logging.loggers.flask]
   handlers = ["stderr"]

   [logging.loggers."urllib.request"]
   handlers = ["stderr"]

   [logging.loggers.werkzeug]
   handlers = ["stderr"]

   [logging.handlers.stderr]
   class = "logging.StreamHandler"
   level = "INFO"
   stream = "ext://sys.stderr"

"""
import logging.config

from ..base import Configuration

__all__ = 'LoggingConfiguration',


class LoggingConfiguration(Configuration):
    """Hold configuration for :mod:`logging`."""

    def configure_logging(self) -> None:
        """Configure :mod:`logging`."""
        try:
            conf = self.config['logging']
        except KeyError:
            pass
        else:
            logging.config.dictConfig(conf)
