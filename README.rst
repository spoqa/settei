設定 (Settei)
=============

.. image:: https://readthedocs.org/projects/settei/badge/?version=latest
   :target: http://settei.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/settei.svg
   :target: https://badge.fury.io/py/settei

.. image:: https://circleci.com/gh/spoqa/settei.svg?style=svg
    :target: https://circleci.com/gh/spoqa/settei


Configuration utility for common Python applications and services.
FYI, Settei means settings in Japanese. :)


Loading a configuration is easy
-------------------------------

Suppose you use `Flask`_ with Settei.

.. code-block:: python

   from flask import Flask
   from settei import Configuration, config_property

   class WebConfiguration(Configuration):
      """Load Configuration::

         [web]
         debug = true

      """

      #: debug option
      debug = config_property('web.debug', bool, default=False)


   conf = WebConfiguration.from_path(pathlib.Path('.') / 'dev.toml')
   app = Flask(__name__)


   if __name__ == '__main__':
       app.run(debug=conf.debug)


.. _Flask: http://flask.pocoo.org/
