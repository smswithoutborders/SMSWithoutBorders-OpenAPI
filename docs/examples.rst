Examples
########

View errors (if any) from Open API's callback URL
=================================================

.. note::

    This tutorial requires you to have the developer's token (Auth_key and Auth_id) from the SMS Without Borders developer console. If you don't have the developer's token, head over to `SMS Without Borders developer console <https://developers.smswithoutborders.com>`_ and create one. You will also have to set up `Open API <https://github.com/smswithoutborders/SMSWithoutBorders-OpenAPI>`_ and have it running.


Once you have Open API all set up, you can start sending out `single <https://smswithoutborders-openapi.readthedocs.io/en/dev/reference_documentation.html#send-single-sms-message>`_ or `bulk <https://smswithoutborders-openapi.readthedocs.io/en/dev/reference_documentation.html#send-bulk-sms-messages>`_ SMS messages.


In order to actually see the output of the ``callback_url`` in your post request which should look somewhat like this:

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

You can locally set up a tiny Flask app like this and run it

.. code-block:: python

    from flask import Flask, request
    import logging

    app = Flask(__name__)

    logging.basicConfig(level='INFO', format='%(asctime)s-%(levelname)s-%(message)s')

    @app.route("/", methods=['GET', 'POST'])
    def log_openapi_errors():
        if request.method == 'POST':
            error_data = request.get_json()
            logging.error("\033[31m%s\033[00m", error_data)
            return error_data
        return "<h1>Check your logs to see if you got errors</h1>"


    if __name__=='__main__':
        app.run(debug=True)

Once your tiny Flask app is running, add it's localhost URL as the value of the ``callback_url`` of your Open API post request.

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
    "callback_url": "http://127.0.0.1:5000",
    "uuid": ""
    }'

From now when you send a post request to Open API, you can now check the logs of your tiny Flask app to see the the result of the callback URL. It should return an array of json objects if there happen to be any errors in your post request to Open API. Your error log should look like this:


.. code-block:: bash

    2022-05-11 11:16:31,934-ERROR-{'errors': [{'operator_name': 'MTN Cameroon', 'number': '+2376728-+72885', 'error_message': '(1) The string supplied did not seem to be a phone number.', 'timestamp': '2022-05-11 11:16:31.931214'}], 'uuid': '6d6b83e2-d113-13ec-ae9a-cba900762ab3'}
