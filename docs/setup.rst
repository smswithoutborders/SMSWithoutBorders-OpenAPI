How to setup OpenAPI
####################

Setup configuration file
========================

The configuration file is located in the ``config`` directory.

.. code-block:: bash

    cp config/example.default.ini default.ini

Link OpenAPI to SMSWithoutBorders developer's console
=====================================================

In the configuration file ``default.ini``, the section ``DEVELOPER`` is to setup SMSWithoutBorders developer's console.

1. HOST: The url pointing to SMSWithoutBorders developer's console (without port number)
2. PORT: The port number SMSWithoutBorders developer's console connects to.
3. VERSION: The version number of SMSWithoutBorders developer's console you're trying to connect to. Prefix the version number with a "v". Example v1, v2, e.t.c 


Setup access credentials
========================

Access credentials are found in the root directory of the repository named ``setup.ini``.

.. code-block:: bash

    cp example.setup.ini setup.ini

.. note::

    The values of your access credentials most match those of the SMSWithoutBorders developer's console you're connecting to else connection will be denied.
