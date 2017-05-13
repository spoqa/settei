""":mod:`settei` --- App object holding configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2016---2017 Spoqa, Inc.
:license: Apache License 2.0, see LICENSE for more details.

"""
from .base import Configuration, ConfigWarning, config_property
from .version import VERSION

__all__ = 'Configuration', 'ConfigWarning', 'config_property'
__version__ = VERSION
