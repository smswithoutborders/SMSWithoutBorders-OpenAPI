import logging
import requests

from flask import Blueprint, helpers, jsonify, request
from error import BadRequest, Conflict, InternalServerError, Unauthorized
from configparser import ConfigParser
from RabbitMQ.src.rabbitmq import RabbitMQ
from routes.helpers import (
    InvalidCountryCode,
    InvalidPhoneNUmber,
    MissingCountryCode,
    get_phonenumber_country,
)

logger = logging.getLogger(__name__)
v1 = Blueprint("v1", __name__)


@v1.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        if not "auth_id" in request.json or not request.json["auth_id"]:
            logger.error("no auth_id")
            raise BadRequest()
        elif not "auth_key" in request.json or not request.json["auth_key"]:
            logger.error("no auth_key")
            raise BadRequest()
        elif not "key" in request.json or not request.json["key"]:
            logger.error("no key")
            raise BadRequest()
        elif not "id" in request.json or not request.json["id"]:
            logger.error("no id")
            raise BadRequest()

        AUTH_ID = request.json["auth_id"]
        AUTH_KEY = request.json["auth_key"]
        ID = request.json["id"]
        KEY = request.json["key"]

        setup = ConfigParser()
        setup.read("setup.ini")
        SETUP = setup["CREDENTIALS"]
        SETUP_ID = SETUP["ID"]
        SETUP_KEY = SETUP["key"]

        developer = ConfigParser()
        developer.read("config/default.ini")
        DEVELOPER = developer["DEVELOPER"]
        DEVELOPER_HOST = DEVELOPER["HOST"]
        DEVELOPER_PORT = DEVELOPER["PORT"]
        DEVELOPER_VERSION = DEVELOPER["VERSION"]
        DEVELOPER_URL = (
            f"{DEVELOPER_HOST}:{DEVELOPER_PORT}/{DEVELOPER_VERSION}/authenticate"
        )

        if ID != SETUP_ID and KEY != SETUP_KEY:
            logger.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()
        else:
            data = {"auth_id": AUTH_ID, "auth_key": AUTH_KEY}
            response = requests.post(url=DEVELOPER_URL, json=data)
            if response.status_code == 200:
                r = RabbitMQ(dev_id=AUTH_ID)
                try:
                    if r.exist():
                        logger.error("USER IS SUBSCRIBED ALREADY")
                    else:
                        r.add_user(dev_key=AUTH_KEY)
                except Exception as error:
                    raise error
                return "", 200
            elif response.status_code == 401:
                logger.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                raise Unauthorized()
    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except Conflict as err:
        return str(err), 409
    except (InternalServerError) as err:
        logger.error(err)
        return "internal server error", 500
    except (Exception) as err:
        logger.error(err)
        return "internal server error", 500


@v1.route("/unsubscribe", methods=["DELETE"])
def unsubscribe():
    try:
        if not "auth_id" in request.json or not request.json["auth_id"]:
            logger.error("no auth_id")
            raise BadRequest()
        elif not "auth_key" in request.json or not request.json["auth_key"]:
            logger.error("no auth_key")
            raise BadRequest()
        elif not "key" in request.json or not request.json["key"]:
            logger.error("no key")
            raise BadRequest()
        elif not "id" in request.json or not request.json["id"]:
            logger.error("no id")
            raise BadRequest()

        AUTH_ID = request.json["auth_id"]
        AUTH_KEY = request.json["auth_key"]
        ID = request.json["id"]
        KEY = request.json["key"]

        setup = ConfigParser()
        setup.read("setup.ini")
        SETUP = setup["CREDENTIALS"]
        SETUP_ID = SETUP["ID"]
        SETUP_KEY = SETUP["key"]

        developer = ConfigParser()
        developer.read("config/default.ini")
        DEVELOPER = developer["DEVELOPER"]
        DEVELOPER_HOST = DEVELOPER["HOST"]
        DEVELOPER_PORT = DEVELOPER["PORT"]
        DEVELOPER_VERSION = DEVELOPER["VERSION"]
        DEVELOPER_URL = (
            f"{DEVELOPER_HOST}:{DEVELOPER_PORT}/{DEVELOPER_VERSION}/authenticate"
        )

        if ID != SETUP_ID and KEY != SETUP_KEY:
            logger.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()
        else:
            data = {"auth_id": AUTH_ID, "auth_key": AUTH_KEY}
            response = requests.post(url=DEVELOPER_URL, json=data)
            if response.status_code == 200:
                r = RabbitMQ(dev_id=AUTH_ID)
                try:
                    if r.exist():
                        r.delete()
                    else:
                        logger.error("USER IS NOT SUBSCRIBED")
                except Exception as error:
                    raise error
                return "", 200
            elif response.status_code == 401:
                logger.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                raise Unauthorized()
    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except (InternalServerError) as err:
        logger.error(err)
        return "internal server error", 500
    except (Exception) as err:
        logger.error(err)
        return "internal server error", 500


@v1.route("/sms", methods=["POST"])
def sms():
    try:
        if not "auth_id" in request.json or not request.json["auth_id"]:
            logger.error("no auth_id")
            raise BadRequest()
        elif not "data" in request.json:
            logger.error("no data")
            raise BadRequest()
        elif not isinstance(request.json["data"], list):
            logger.error("Data most be a list")
            raise BadRequest()

        payload = request.json["data"]
        AUTH_ID = request.json["auth_id"]

        for data in payload:
            TEXT = data["text"]
            NUMBER = data["number"]
            OPERATOR = data["operator_name"]

            sms_data = {
                "operator_name": OPERATOR,
                "text": TEXT,
                "number": NUMBER,
            }

            r = RabbitMQ(dev_id=AUTH_ID)
            try:
                if r.exist():
                    r.request_sms(data=sms_data)
                else:
                    logger.error("USER IS NOT SUBSCRIBED")
                    raise Unauthorized()
            except Exception as error:
                raise error
        return "", 200

    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except Conflict as err:
        return str(err), 409
    except (InternalServerError) as err:
        logger.error(err)
        return "internal server error", 500
    except (Exception) as err:
        logger.error(err)
        return "internal server error", 500


@v1.route("/sms/operators", methods=["POST"])
def sms_operator():
    try:
        if not isinstance(request.json, list):
            logger.error("Request body most be a list")
            raise BadRequest()

        payload = request.json
        result = []

        for data in payload:
            TEXT = data["text"]
            NUMBER = data["number"]

            if not "operator_name" in data or not data["operator_name"]:
                OPERATOR = ""
            else:
                OPERATOR = data["operator_name"]

            payload_data = {"number": NUMBER, "text": TEXT, "operator_name": OPERATOR}

            try:
                if not OPERATOR:
                    operator = get_phonenumber_country(NUMBER)
                    payload_data["operator_name"] = operator
                    result.append(payload_data)
                else:
                    result.append(payload_data)
            except InvalidPhoneNUmber as error:
                logger.error(f"INVALID PHONE NUMBER: {NUMBER}")
                result.append(payload_data)
            except InvalidCountryCode as error:
                logger.error(f"INVALID COUNTRY CODE: {NUMBER}")
                result.append(payload_data)
            except MissingCountryCode as error:
                logger.error(f"MISSING COUNTRY CODE: {NUMBER}")
                result.append(payload_data)

        return jsonify(result), 200

    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except InternalServerError as err:
        logger.error(err)
        return "internal server error", 500
    except Exception as err:
        logger.error(err)
        return "internal server error", 500
