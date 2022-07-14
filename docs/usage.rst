Usage
#####

Connect Gateway Client
======================

.. note::

    This tutorial requires you to have the developer's token (Auth_key and Auth_id) from the SMS Without Borders developer console. If you don't have the developer's token, head over to `SMS Without Borders developer console <https://developers.smswithoutborders.com>`_ and create one.

.. note::

    This tutorial also requires you to have a copy of the `SMS Without Borders Gateway client <https://github.com/smswithoutborders/SMSWithoutBorders-Gateway-Client>`_ set up on your device. If you do not have a copy of the `SMS Without Borders Gateway client <https://github.com/smswithoutborders/SMSWithoutBorders-Gateway-Client>`_ set up on your device, head over to `SMS Without Borders Gateway Client <https://github.com/smswithoutborders/SMSWithoutBorders-Gateway-Client>`_ and set it up

Having acquired your SMS Without Borders developer's token (Auth_key and Auth_id) and a copy of the SMS Without Borders Gateway client setup on your device, you can now connect OpenAPI to your gateway client's instance in a few steps. 

1. Configure your gateway client
********************************

The configuration file (`config.ini <https://github.com/smswithoutborders/SMSWithoutBorders-Gateway-Client/blob/alpha_stable/.configs/example.config.ini>`_) is located in the `.configs <https://github.com/smswithoutborders/SMSWithoutBorders-Gateway-Client/tree/alpha_stable/.configs>`_ directory of your gateway client's directory. Place your developer's token (Auth_key and Auth_id) under the ``[NODE]`` section of your configuration file.

.. code-block:: ini

    [OPENAPI]
    api_id=
    api_key=

also configure the ``connection_url`` to point the server you're trying to conect to. To connect to the SMSWithoutBorders server use ``developers.smswithoutborders.com``

.. code-block:: ini

    connection_url=developers.smswithoutborders.com

.. note::

    The ``connection_url`` can be your custom server visit `RabbitMQ <https://github.com/smswithoutborders/SMSWithoutBorders-Product-deps-RabbitMQ#rabbitmq-for-openapi>`_ to set-up your instance.

2. Restart your gateway client
******************************

You will need to restart your gateway and cluster for changes to take effect. In the root of the repo use the command: 

.. code-block:: bash

    make restart

All done!
*********

You are now ready to send out bulk SMS messages with OpenAPI. Head over to your API agent and send out bulk SMS messages with your developer's token.

Example using `curl <https://curl.se/>`_

.. code-block:: bash

    curl --location --request POST 'https://developers.smswithoutborders.com:14000/v1/sms' \
    --header 'Content-Type: application/json' \
    --data-raw '{
    "auth_id":"",
    "data": [{
        "operator_name":"",
        "text":"",
        "number":""
        }]
    }'

See :ref:`Reference Documentation` for more API references

Manage OpenAPI messages
=======================

Manage your OpenApi messages through the `SMSWithoutBorders RabbitMQ dashboard <https://developers.smswithoutborders.com:15671>`_. 

1. Login
********

Visit `SMSWithoutBorders RabbitMQ dashboard <https://developers.smswithoutborders.com:15671>`_.

.. image:: https://raw.githubusercontent.com/smswithoutborders/SMSWithoutBorders-Resources/master/multimedia/img/rabbitmq_login.png
    :width: 350
    :align: center
    :alt: rabbitmq_login

- Username = Your developer's auth_id
- Password = Your developer's auth_key

.. note:: 

    If you do not have the developer's token (Auth_key and Auth_id), head over to `SMS Without Borders developer console <https://developers.smswithoutborders.com>`_ and create one.
