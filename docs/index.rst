.. settei documentation master file, created by
   sphinx-quickstart on Thu Apr 21 02:05:52 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to settei's documentation!
==================================

Configuration utility for common Python applications and services.


Load configuration from ``dev.toml``.

.. code-block:: python

   import pathlib

   from settei import Configuration, config_property

   class WebConfiguration(Configuration):
       """Load Configuration::

          [web]
          debug = true

       """

       #: debug option
       debug = config_property('web.debug', bool, default=False)


   conf = WebConfiguration.from_path(pathlib.Path('.') / 'dev.toml')
   print(conf.debug)


Contents:

.. toctree::
   :maxdepth: 2

   settei



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

