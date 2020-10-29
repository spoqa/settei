Changelog
=========

Version 0.7.3
-------------

Released on October 29, 2020.

- Fix bug that cannot set `config_object_property` from environment variables.

Version 0.7.2
-------------

Released on October 26, 2020.

- Exclude `tests` module from package.
- To be able to get an environment value from `Configuration` itself
  as well as getting from `config_property`.

Version 0.7.1
-------------

Released on March 18, 2020.

- Support values recursively inside lists from environment variable.

Version 0.7.0
-------------

Released on March 02, 2020.

- Removed ``env_name`` paramter from
  :class:`~settei.base.config_object_property`.
- Changed asterisk charater into ``ASTERISK``. We couldn't use special
  charaters in OS environment variable name.
- Support list in environment variable.
- Allow configure value on both toml and environment variable at
  the same time.  Firstly settei get a configuration from toml,
  then scan an environment variable.

Version 0.6.0
-------------

Released on February 28, 2020.

- Added ``lookup_env`` option to :class:`~settei.base.config_object_property`.
  It giaves you the way to read OS environment variable like
  :class:`~settei.base.config_property`. [`#37`_]

.. _#37: https://github.com/spoqa/settei/pull/37

Version 0.5.6
-------------

Released on February 25, 2020.

- Added ``lookup_env`` option to :class:`~settei.base.config_property`.
  It gives you the way to read OS environment variable on settei. [`#35`_]

.. _#35: https://github.com/spoqa/settei/pull/35

Version 0.5.5
-------------

Released on December 5, 2019.

- Fix ``default`` option of :class:`~settei.base.config_object_property`. [`#34`_]

.. _#34: https://github.com/spoqa/settei/pull/34

Version 0.5.4
-------------

Released on October 29, 2019.

- Add ``cache`` option to :class:`~settei.base.config_object_property`.

.. _#27: https://github.com/spoqa/settei/pull/27
.. _#32: https://github.com/spoqa/settei/pull/32

Version 0.5.3
-------------

Released on June 20, 2019.

- Change the ``app`` argument type of :attr:`~settei.presets.flask.WebConfiguration.on_web_loaded`
  to :class:`typing.Callable` from :class:`flask.Flask`. [`#31`_]

.. _#31: https://github.com/spoqa/settei/pull/31

Version 0.5.2
-------------

Released on June 10, 2019.

- Enabled declaring :class:`enum.Enum` types in :class:`~settei.config_proprety`. [`#29`_]
- Add hooks list feature for :attr:`~settei.presets.flask.WebConfiguration.on_web_loaded` and
  :attr:`~settei.presets.celery.WorkerConfiguration.on_worker_loaded`. [`#30`_]

.. _#29: https://github.com/spoqa/settei/pull/29
.. _#30: https://github.com/spoqa/settei/pull/30


Version 0.5.1
-------------

Released on Sep 11, 2018.

- Became to support Python 3.7.  [`#25`_, `#28`_]

.. _#25: https://github.com/spoqa/settei/issues/25
.. _#28: https://github.com/spoqa/settei/pull/28


Version 0.5.0
-------------

Released on July 24, 2017.

- Added ``recurse`` option to :class:`~settei.base.config_object_property`.
  If it's :const:`True` nested tables are also evaluated.  :const:`False` by
  default for backward compatibility.


Verison 0.4.0
-------------

Released on May 14, 2017.

- :class:`~settei.base.config_object_property` was added.  It's a kind of
  dependency injection, but very limited version.

- :exc:`~settei.base.ConfigError`, :exc:`~settei.base.ConfigKeyError`,
  :exc:`~settei.base.ConfigTypeError`, and :exc:`~settei.base.ConfigValueError`.

  Prior to 0.4.0, :class:`~settei.base.Configuration` had raised Python's
  built-in :exc:`KeyError` on missing keys, but since 0.4.0 it became to raise
  :exc:`~settei.base.ConfigKeyError`, a subtype of :exc:`KeyError`, instead.

  In the same manner, while prior to 0.4.0, it had raised Python's
  built-in :exc:`TypeError` when a configured value is not of a type it expects,
  but since 0.4.0 it became to raise :exc:`~settei.base.ConfigTypeError`
  instead.  :exc:`~settei.base.ConfigTypeError` is also a subtype of
  :class:`TypeError`.


Version 0.3.0
-------------

Released on January 22, 2017.

- As tsukkomi_ is now abandoned, it's replaced by typeguard_.

.. _typeguard: https://github.com/agronholm/typeguard


Version 0.2.2
-------------

Released on November 18, 2016.  Note that the version 0.2.1 has never been
released due to our mistake on versioning.

- :class:`~settei.presets.celery.WorkerConfiguration` became to have
  :attr:`~settei.presets.celery.WorkerConfiguration.worker_schedule`
  config property to configure Celery beat --- Celery's periodic tasks.


Version 0.2.0
-------------

Released on July 13, 2016.

- :mod:`settei` became a package (had been a module), which contains
  :mod:`settei.base` module.
- :class:`settei.Configuration`, :class:`settei.ConfigWarning`, and
  :class:`settei.config_property` were moved to :mod:`settei.base` module.
  Although aliases for these previous import paths will be there for a while,
  we recommend to import them from :mod:`settei.base` mdoule since they are
  deprecated.

- Presets were introduced: :mod:`settei.presets`.

  - :mod:`settei.presets.celery` is for configuring Celery_ apps.
  - :mod:`settei.presets.flask` is for configuring Flask_ web apps.
  - :mod:`settei.presets.logging` is for configuring Python standard
    :mod:`logging` system.

- :mod:`settei.version` module was added.
- typeannotations_ was replaced by tsukkomi_.
- Settei now requires pytoml_ 0.1.10 or higher.  (It had required 0.1.7 or
  higher.)

.. _Celery: http://www.celeryproject.org/
.. _flask: http://flask.pocoo.org/
.. _typeannotations: https://github.com/ceronman/typeannotations
.. _tsukkomi: https://github.com/spoqa/tsukkomi
.. _pytoml: https://github.com/avakar/pytoml


Version 0.1.1
-------------

Released on April 15, 2016.

- :class:`settei.base.config_property` became to support :data:`typing.Union`
  type.


Version 0.1.0
-------------

Released on April 1, 2016.  Initial release.
