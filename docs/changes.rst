Changlog
========

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
