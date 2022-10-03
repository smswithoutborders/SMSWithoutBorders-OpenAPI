Reference Documentation
#######################

Service endpoint
================

A service endpoint is a base URL that specifies the network address of an API service. One service might have multiple service endpoints. This service has the following service endpoint and all URIs below are relative to this service endpoint:

- ``https://developers.smswithoutborders.com:14000``

API V1 Endpoints
================

.. list-table::
    :widths: auto

    * - Action
      - Endpoint
      - Parameters
      - Request body

    * - :ref:`Send SMS<Send single SMS message>`
      - POST /v1/sms
      - None
      - * auth_id = STRING
        * data = [{text = STRING, number = STRING, operator_name = STRING}]
        * callback_url = STRING
        * uuid = STRING
    
    * - :ref:`Get Phone number operator name<Get Phone Number operator name>`
      - POST /v1/sms/operators
      - None
      - * [{text = STRING, number = STRING, operator_name = STRING}]

    * - :ref:`Update message status<Update message status>`
      - PUT /v1/metrics/<uid>
      - * uid = STRING
      - * [{status = STRING, message = STRING}]

.. warning::

    We advise you to use this endpoint safely in the back-end to avoid exposing your developer's token to unauthorized persons.

Examples using `curl <https://curl.se/>`_

Send single SMS message
***********************
.. note::

    The ``uuid`` key is any random string provided by the user used to identify the request. If left empty, OpenAPI will populate the ``uuid`` key with a randomly generated uuid.

    The ``callback_url`` will be invoked after the request is complete with a ``POST`` in the form:
    
    .. code-block:: json

        {
            "errors": [{
                "operator_name":"",
                "number":"",
                "error_message": "",
                "timestamp": ""
                }],
            "uuid": ""
        }

    - If the ``errors`` array is empty all messages were requested successfully.
    - ``callback_url`` field accepts multiple urls, seperate each with a comma. Example `"callback_url":"https://example.com,https://example1.com,https://example2.com"`

    The phone number format to be used in the request bodies of the API calls should be `E.164 <https://en.wikipedia.org/wiki/E.164>`_.

.. code-block:: bash

    curl --location --request POST 'https://developers.smswithoutborders.com:14000/v1/sms' \
    --header 'Content-Type: application/json' \
    --data-raw '{
    "auth_id":"",
    "data": [{
        "operator_name":"",
        "text":"",
        "number":""
        }],
    "callback_url": "",
    "uuid": ""
    }'

Send bulk SMS messages
**********************

.. note::

    The ``uuid`` key is any random string provided by the user used to identify the request. If left empty, OpenAPI will populate the ``uuid`` key with a randomly generated uuid.

    The ``callback_url`` will be invoked after the request is complete with a ``POST`` in the form:
    
    .. code-block:: json

        {
            "errors": [{
                "operator_name":"",
                "number":"",
                "error_message": "",
                "timestamp": ""
                }],
            "uuid": ""
        }

    - If the ``errors`` array is empty all messages were requested successfully.
    - ``callback_url`` field accepts multiple urls, seperate each with a comma. Example `"callback_url":"https://example.com,https://example1.com,https://example2.com"`

    The phone number format to be used in the request bodies of the API calls should be `E.164 <https://en.wikipedia.org/wiki/E.164>`_.

.. code-block:: bash

    curl --location --request POST 'https://developers.smswithoutborders.com:14000/v1/sms' \
    --header 'Content-Type: application/json' \
    --data-raw '{
    "auth_id":"",
    "data": [{
        "operator_name":"",
        "text":"",
        "number":""
        },
        {
        "operator_name":"",
        "text":"",
        "number":""
        },
        {
        "operator_name":"",
        "text":"",
        "number":""
        }],
    "callback_url": "",
    "uuid": ""
    }'

Get Phone Number operator name
******************************

If the ``operator_name`` key is an empty string or not present in the request, It will be generated and populated in the response. But if the ``operator_name`` key is present it won't be modified in the response.

.. code-block:: bash

    curl --location --request POST 'https://developers.smswithoutborders.com:14000/v1/sms/operators' \
    --header 'Content-Type: application/json' \
    --data-raw '[
        {
        "operator_name":"",
        "text":"",
        "number":""
        },
        {
        "operator_name":"",
        "text":"",
        "number":""
        },
        {
        "operator_name":"",
        "text":"",
        "number":""
        }
    ]'

Update message status
*********************

There are two steps involved in the update process

1. Authorization
----------------

.. note::
    
    This step requires the user to have an `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_ setup.

The user has to provide the following in the `request body <https://developer.mozilla.org/en-US/docs/Web/API/Request/body>`_:

- Auth key (From an `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_)
- Auth id (From an `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_)

The user also must configure their `header <https://developer.mozilla.org/en-US/docs/Glossary/Representation_header>`_ to:

- `Content-Type <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type>`_ = application/json

Here is an example. Running `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_ locally on port 3000

.. code-block:: bash

    curl --location --request POST 'http://localhost:3000/v1/authenticate' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "auth_key": "",
        "auth_id": ""
    }'

If successful a `cookie <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cookie>`_ is set on the user's agent valid for two hours. The cookie is used to track the user's seesion. Also the `response <https://developer.mozilla.org/en-US/docs/Web/API/Response/body>`_ should have a `status <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>`_ of ``200`` and the body should contain an empty object

.. code-block:: bash

    {}

2. Update status
----------------

.. note::
        
    This step requires the user to have an `SMSWithoutBorders OpenAPI <https://github.com/smswithoutborders/SMSWithoutBorders-OpenAPI>`_ setup and `configured <https://github.com/smswithoutborders/SMSWithoutBorders-OpenAPI/blob/main/docs/CONFIGURATIONS.md#setup>`_ to communitcate with their `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_.

    The user has to make sure `SMSWithoutBorders Developer Back-end server <https://github.com/smswithoutborders/SMSWithoutBorders-Dev-BE>`_ is running.

The user has to provide the following in the `request body <https://developer.mozilla.org/en-US/docs/Web/API/Request/body>`_:

- status (The message status. Either sent, delivered, failed, requested)
- message (Information regarding the message status)

The user also must configure their `header <https://developer.mozilla.org/en-US/docs/Glossary/Representation_header>`_ to:

- `Content-Type <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type>`_ = application/json

Here is an example. Running `SMSWithoutBorders OpenAPI <https://github.com/smswithoutborders/SMSWithoutBorders-OpenAPI>`_ locally on port 4000

.. code-block:: bash

    curl --location --request POST 'http://localhost:4000/v1/metrics/<uid>' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "status": "",
        "message": ""
    }'

If successful the `response <https://developer.mozilla.org/en-US/docs/Web/API/Response/body>`_ should have a `status <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>`_ of ``200``.