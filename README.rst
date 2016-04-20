設定 (settei)
=============

.. image:: https://readthedocs.org/projects/settei/badge/?version=latest
   :target: http://settei.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/settei.svg
   :target: https://badge.fury.io/py/settei

.. image:: https://circleci.com/gh/spoqa/settei.svg?style=svg
    :target: https://circleci.com/gh/spoqa/settei


Configuration utility for common Python applications and services.
FYI, settei means setting in japanese :)


Loading a configuration is easy
-------------------------------

Suppose you use `flask`_ with settei.

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


.. _flask: http://flask.pocoo.org/
