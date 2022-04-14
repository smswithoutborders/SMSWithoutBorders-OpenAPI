import logging
import requests

from flask import Blueprint, jsonify, request
from error import BadRequest, Conflict, InternalServerError, Unauthorized
from config_init import configuration

config = configuration()

from RabbitMQ.src.rabbitmq import RabbitMQ
from routes.helpers import (
    InvalidCountryCode,
    InvalidPhoneNUmber,
    MissingCountryCode,
    get_phonenumber_country,
)
from uuid import uuid1
from datetime import datetime

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

        authId = request.json["auth_id"]
        authKey = request.json["auth_key"]
        devSetupId = request.json["id"]
        devSetupKey = request.json["key"]

        SETUP = config["SETUP_CREDS"]
        setupId = SETUP["ID"]
        setupKey = SETUP["key"]

        DEVELOPER = config["DEVELOPER"]
        developerHost = DEVELOPER["HOST"]
        developerPort = DEVELOPER["PORT"]
        developerVersion = DEVELOPER["VERSION"]
        developerUrl = (
            f"{developerHost}:{developerPort}/{developerVersion}/authenticate"
        )

        if devSetupId != setupId and devSetupKey != setupKey:
            logger.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()
        else:
            data = {"auth_id": authId, "auth_key": authKey}
            response = requests.post(url=developerUrl, json=data)
            if response.status_code == 200:
                r = RabbitMQ(dev_id=authId)
                try:
                    if r.exist():
                        logger.error("USER IS SUBSCRIBED ALREADY")
                    else:
                        r.add_user(dev_key=authKey)
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

        authId = request.json["auth_id"]
        authKey = request.json["auth_key"]
        devSetupId = request.json["id"]
        devSetupKey = request.json["key"]

        SETUP = config["SETUP_CREDS"]
        setupId = SETUP["ID"]
        setupKey = SETUP["key"]

        DEVELOPER = config["DEVELOPER"]
        developerHost = DEVELOPER["HOST"]
        developerPort = DEVELOPER["PORT"]
        developerVersion = DEVELOPER["VERSION"]
        developerUrl = (
            f"{developerHost}:{developerPort}/{developerVersion}/authenticate"
        )

        if devSetupId != setupId and devSetupKey != setupKey:
            logger.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()
        else:
            data = {"auth_id": authId, "auth_key": authKey}
            response = requests.post(url=developerUrl, json=data)
            if response.status_code == 200:
                r = RabbitMQ(dev_id=authId)
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
        authId = request.json["auth_id"]

        if not "callback_url" in request.json or not request.json["callback_url"]:
            callbackUrl = ""
        else:
            callbackUrl = request.json["callback_url"]

        if not "uuid" in request.json or not request.json["uuid"]:
            req_uuid = uuid1()
        else:
            req_uuid = request.json["uuid"]

        errors = []

        for data in payload:
            text = data["text"]
            number = data["number"]
            operatorName = data["operator_name"]

            sms_data = {
                "operator_name": operatorName,
                "text": text,
                "number": number,
            }

            r = RabbitMQ(dev_id=authId)
            try:
                if r.exist():
                    r.request_sms(data=sms_data)
                else:
                    logger.error("USER IS NOT SUBSCRIBED")
                    raise Unauthorized()
            except Exception as error:
                logger.error(error)
                err_data = {
                    "operator_name": operatorName,
                    "number": number,
                    "error_message": str(error),
                    "timestamp": str(datetime.now()),
                }
                errors.append(err_data)

        result = {"errors": errors, "uuid": str(req_uuid)}

        if len(callbackUrl) > 0:
            try:
                requests.post(url=callbackUrl, json=result)
            except Exception as err:
                logger.error(err)

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
            text = data["text"]
            number = data["number"]

            if not "operator_name" in data or not data["operator_name"]:
                operatorName = ""
            else:
                operatorName = data["operator_name"]

            payload_data = {
                "number": number,
                "text": text,
                "operator_name": operatorName,
            }

            try:
                if not operatorName:
                    operator = get_phonenumber_country(number)
                    payload_data["operator_name"] = operator
                    result.append(payload_data)
                else:
                    result.append(payload_data)
            except InvalidPhoneNUmber as error:
                logger.error(f"INVALID PHONE NUMBER: {number}")
                result.append(payload_data)
            except InvalidCountryCode as error:
                logger.error(f"INVALID COUNTRY CODE: {number}")
                result.append(payload_data)
            except MissingCountryCode as error:
                logger.error(f"MISSING COUNTRY CODE: {number}")
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
