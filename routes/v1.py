import logging

from flask import Blueprint, jsonify, request
from error import BadRequest, Conflict, InternalServerError, Unauthorized
from configparser import ConfigParser
from RabbitMQ.src.rabbitmq import RabbitMQ
import requests

LOG = logging.getLogger(__name__)
v1 = Blueprint("v1", __name__)


@v1.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        if not "auth_id" in request.json or not request.json["auth_id"]:
            LOG.error("no auth_id")
            raise BadRequest()
        elif not "auth_key" in request.json or not request.json["auth_key"]:
            LOG.error("no auth_key")
            raise BadRequest()
        elif not "key" in request.json or not request.json["key"]:
            LOG.error("no key")
            raise BadRequest()
        elif not "id" in request.json or not request.json["id"]:
            LOG.error("no id")
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
            LOG.error("INVALID SETUP CREDENTIALS")
            raise Unauthorized()
        else:
            data = {"auth_id": AUTH_ID, "auth_key": AUTH_KEY}
            response = requests.post(url=DEVELOPER_URL, json=data)
            if response.status_code == 200:
                r = RabbitMQ(dev_id=AUTH_ID)
                try:
                    if r.exist():
                        LOG.error("USER IS SUBSCRIBED ALREADY")
                    else:
                        r.add_user(dev_key=AUTH_KEY)
                except Exception as error:
                    raise error
                return "", 200
            elif response.status_code == 401:
                LOG.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                raise Unauthorized()
    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except Conflict as err:
        return str(err), 409
    except (InternalServerError) as err:
        LOG.error(err)
        return "internal server error", 500
    except (Exception) as err:
        LOG.error(err)
        return "internal server error", 500


@v1.route("/unsubscribe", methods=["DELETE"])
def unsubscribe():
    try:
        if not "auth_id" in request.json or not request.json["auth_id"]:
            LOG.error("no auth_id")
            raise BadRequest()
        elif not "auth_key" in request.json or not request.json["auth_key"]:
            LOG.error("no auth_key")
            raise BadRequest()
        elif not "key" in request.json or not request.json["key"]:
            LOG.error("no key")
            raise BadRequest()
        elif not "id" in request.json or not request.json["id"]:
            LOG.error("no id")
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
            LOG.error("INVALID SETUP CREDENTIALS")
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
                        LOG.error("USER IS NOT SUBSCRIBED")
                except Exception as error:
                    raise error
                return "", 200
            elif response.status_code == 401:
                LOG.error("INVALID DEVELOPERS AUTH_KEY AND AUTH_ID")
                raise Unauthorized()
    except BadRequest as err:
        return str(err), 400
    except Unauthorized as err:
        return str(err), 401
    except (InternalServerError) as err:
        LOG.error(err)
        return "internal server error", 500
    except (Exception) as err:
        LOG.error(err)
        return "internal server error", 500
