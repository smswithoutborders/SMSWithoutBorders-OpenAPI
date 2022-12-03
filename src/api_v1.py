import logging
import requests
import json
from base64 import b64decode
from uuid import uuid1
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

from settings import Configurations
setupId = Configurations.ID
setupKey = Configurations.KEY
developerHost = Configurations.DEV_HOST
developerPort = Configurations.DEV_PORT
developerVersion = Configurations.DEV_VERSION
dev_cookie_name = Configurations.DEV_COOKIE_NAME

from flask import Blueprint
from flask import jsonify
from flask import request

from src.RabbitmqHandler import RabbitMQ

from src.PhoneNumberHandler import InvalidCountryCode, InvalidPhoneNUmber, NotE164PhoneNumberFormat, MissingCountryCode, get_phonenumber_country_code, check_phonenumber_E164, get_phonenumber_carrier_name

from src.models.metrics import Metric_Model
from src.models.sessions import Session_Model
from src.models.twilio import Twilio_Model

v1 = Blueprint("v1", __name__)
dev_v1 = Blueprint("dev_v1", __name__)

from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import Unauthorized
from werkzeug.exceptions import Conflict
from werkzeug.exceptions import Forbidden

@v1.route("/subscribe", methods=["POST"])
def subscribe():
    """
    """
    try:
        if not request.json.get("auth_id"):
            logger.error("no auth_id")
            raise BadRequest()
        elif not request.json.get("auth_key"):
            logger.error("no auth_key")
            raise BadRequest()
        elif not request.json.get("key"):
            logger.error("no key")
            raise BadRequest()
        elif not request.json.get("id"):
            logger.error("no id")
            raise BadRequest()

        authId = request.json["auth_id"]
        authKey = request.json["auth_key"]
        devSetupId = request.json["id"]
        devSetupKey = request.json["key"]

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

    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500

@v1.route("/unsubscribe", methods=["DELETE"])
def unsubscribe():
    """
    """
    try:
        if not request.json.get("auth_id"):
            logger.error("no auth_id")
            raise BadRequest()
        elif not request.json.get("auth_key"):
            logger.error("no auth_key")
            raise BadRequest()
        elif not request.json.get("key"):
            logger.error("no key")
            raise BadRequest()
        elif not request.json.get("id"):
            logger.error("no id")
            raise BadRequest()

        authId = request.json["auth_id"]
        authKey = request.json["auth_key"]
        devSetupId = request.json["id"]
        devSetupKey = request.json["key"]

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
        
    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500

@v1.route("/sms", methods=["POST"])
def sms():
    """
    """
    try:
        if not request.json.get("auth_id"):
            logger.error("no auth_id")
            raise BadRequest()
        elif not request.json.get("data"):
            logger.error("no data")
            raise BadRequest()
        elif not isinstance(request.json["data"], list):
            logger.error("Data most be a list")
            raise BadRequest()

        payload = request.json["data"]
        authId = request.json["auth_id"]

        Metrics = Metric_Model()

        callbackUrl = request.json.get("callback_url")
        req_uuid = request.json.get("uuid") or str(uuid1())
        account_sid = request.json.get("twilio_account_sid")
        auth_token = request.json.get("twilio_auth_token")
        service_sid = request.json.get("twilio_service_sid")
        _from = request.json.get("twilio_from")
        whitelist = request.json.get("whitelist") or []

        if not isinstance(request.json["whitelist"], list):
            logger.error("whitelist most be a list")
            raise BadRequest()

        errors = []

        r = RabbitMQ(dev_id=authId)

        if r.exist():
            for data in payload:
                text = data["text"]
                number = data["number"]

                country_code = "+" + get_phonenumber_country_code(number)

                if account_sid and auth_token and (service_sid or _from) and country_code not in whitelist:
                    try:
                        Twilio = Twilio_Model(
                            account_sid=account_sid,
                            auth_token=auth_token,
                            service_sid=service_sid,
                            _from = _from
                        )

                        sms_data = {
                            "text": text,
                            "number": number,
                        }

                        Twilio.message(number=sms_data["number"], text=sms_data["text"])

                    except Exception as error:
                        logger.error(error)

                        err_data = {
                            "id": "",
                            "operator_name": "",
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }

                        errors.append(err_data)

                else:
                    sms_data = {
                        "uid": str(uuid4()),
                        "operator_name": get_phonenumber_carrier_name(number),
                        "text": text,
                        "number": number,
                    }

                    try:
                        check_phonenumber_E164(number)
                        r.request_sms(data=sms_data)
                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="requested",
                            message="SMS has been successfully requested",
                            auth_id=authId
                        )
                        
                    except InvalidPhoneNUmber as error:
                        logger.error(error)

                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="failed",
                            message=str(error),
                            auth_id=authId
                        )

                        err_data = {
                            "id": sms_data["uid"],
                            "operator_name": sms_data["operator_name"],
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }
                        
                        errors.append(err_data)

                    except InvalidCountryCode as error:
                        logger.error(error)

                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="failed",
                            message=str(error),
                            auth_id=authId
                        )

                        err_data = {
                            "id": sms_data["uid"],
                            "operator_name": sms_data["operator_name"],
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }
                        
                        errors.append(err_data)

                    except MissingCountryCode as error:
                        logger.error(error)
                        
                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="failed",
                            message=str(error),
                            auth_id=authId
                        )

                        err_data = {
                            "id": sms_data["uid"],
                            "operator_name": sms_data["operator_name"],
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }

                        errors.append(err_data)

                    except NotE164PhoneNumberFormat as error:
                        logger.error(error)
                        
                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="failed",
                            message=str(error),
                            auth_id=authId
                        )

                        err_data = {
                            "id": sms_data["uid"],
                            "operator_name": sms_data["operator_name"],
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }

                        errors.append(err_data)

                    except Exception as error:
                        logger.error(error)

                        Metrics.create(
                            uid=sms_data["uid"],
                            phone_number=sms_data["number"],
                            operator_name=sms_data["operator_name"],
                            status="failed",
                            message="An unexpected error has occurred. Please contact your system administrator.",
                            auth_id=authId
                        )

                        err_data = {
                            "id": sms_data["uid"],
                            "operator_name": sms_data["operator_name"],
                            "number": sms_data["number"],
                            "error_message": str(error),
                            "timestamp": str(datetime.now()),
                        }

                        errors.append(err_data)

            result = {"errors": errors, "uuid": req_uuid}

            if callbackUrl:
                callbacks = callbackUrl.split(",")

                for callback in callbacks:
                    try:
                        requests.post(url=callback.strip(), json=result)
                    except Exception as err:
                        logger.error(err)

            return "", 200
                    
        else:
            logger.error("USER IS NOT SUBSCRIBED")
            raise Unauthorized()

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except Conflict as err:
        return str(err), 409

    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500

@v1.route("/sms/operators", methods=["POST"])
def sms_operator():
    """
    """
    try:
        if not isinstance(request.json, list):
            logger.error("Request body most be a list")
            raise BadRequest()

        payload = request.json
        result = []

        for data in payload:
            number = data["number"]

            text = data.get("text") or ""
            operatorName = data.get("operator_name") or ""

            payload_data = {
                "number": number,
                "text": text,
                "operator_name": operatorName,
            }

            try:
                if not operatorName:
                    operator = get_phonenumber_carrier_name(number)
                    payload_data["operator_name"] = operator
                    result.append(payload_data)

                else:
                    result.append(payload_data)

            except InvalidPhoneNUmber:
                logger.error("INVALID PHONE NUMBER: %s" % number)
                result.append(payload_data)

            except InvalidCountryCode:
                logger.error("INVALID COUNTRY CODE: %s" % number)
                result.append(payload_data)

            except MissingCountryCode:
                logger.error("MISSING COUNTRY CODE: %s" % number)
                result.append(payload_data)

        return jsonify(result), 200

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500

@v1.route("/metrics", methods=["POST", "PUT"])
def metrics():
    """
    """
    try:
        method = request.method.lower()

        Metrics = Metric_Model()

        if not request.json.get("auth_id"):
            logger.error("no auth_id")
            raise BadRequest()
        elif not request.json.get("auth_key"):
            logger.error("no auth_key")
            raise BadRequest()
        elif not request.json.get("key"):
            logger.error("no key")
            raise BadRequest()
        elif not request.json.get("id"):
            logger.error("no id")
            raise BadRequest()

        authId = request.json["auth_id"]
        authKey = request.json["auth_key"]
        devSetupId = request.json["id"]
        devSetupKey = request.json["key"]

        developerUrl = (
            f"{developerHost}:{developerPort}/{developerVersion}/authenticate"
        )

        if devSetupId != setupId and devSetupKey != setupKey:
            logger.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()

        else:
            if method == "post":
                data = {"auth_id": authId, "auth_key": authKey}
                response = requests.post(url=developerUrl, json=data)

                if response.status_code == 200:
                    data = Metrics.find(auth_id=authId)

                    return jsonify(data), 200

                elif response.status_code == 401:
                    logger.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                    raise Unauthorized()

            elif method == "put":
                data = {"auth_id": authId, "auth_key": authKey}
                response = requests.post(url=developerUrl, json=data)

                if response.status_code == 200:
                    if not request.json.get("old_auth_id"):
                        logger.error("no old_auth_id")
                        raise BadRequest()

                    old_auth_id = request.json["old_auth_id"]
                   
                    Metrics.update(
                        auth_id=old_auth_id, 
                        new_auth_id=authId
                    )

                    return "", 200

                elif response.status_code == 401:
                    logger.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                    raise Unauthorized()

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500

@dev_v1.before_request
def check_request_origin():
    """
    """
    try:
        origin = request.remote_addr
        if origin not in ['127.0.0.1']:
            logger.error("'%s' tried to access an internal route" % origin)
            raise Forbidden()
        else:
            logger.info("RemoteIp: %s" % origin)

    except Forbidden as err:
        return str(err), 403

    except Exception as error:
        logger.exception(error)
        return "internal server error", 500

@dev_v1.route("/metrics/<string:uid>", methods=["PUT"])
def updateMetricStatus(uid):
    """
    """
    try:
        if not request.cookies.get(dev_cookie_name):
            logger.error("No dev cookie")
            raise Unauthorized()
        elif not request.json.get("status"):
            logger.error("No status provided")
            raise Unauthorized()
        elif request.json["status"] not in ["requested", "failed", "delivered", "sent"]:
            logger.error("Invalid status '%s'" % request.json["status"])
            raise Unauthorized()
        elif not request.json.get("message"):
            logger.error("No message provided")
            raise Unauthorized()

        status = request.json["status"]
        message = request.json["message"]
        
        dev_cookie = json.loads(b64decode(request.cookies.get(dev_cookie_name)))
        dev_uid = dev_cookie["uid"]
        dev_user_agent = dev_cookie["userAgent"]
        dev_verification_path = dev_cookie["verification_path"]

        Session = Session_Model()
        Metrics = Metric_Model()

        Session.authenticate(
            uid=dev_uid,
            user_agent=dev_user_agent,
            cookie=dev_cookie["cookie"],
            verification_path=dev_verification_path
        )

        Metrics.update(
            uid=uid,
            status=status,
            message=message
        )

        return "", 200

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except InternalServerError as err:
        logger.exception(err)
        return "internal server error", 500

    except Exception as err:
        logger.exception(err)
        return "internal server error", 500