import logging
logger = logging.getLogger(__name__)

from config_init import configuration
config = configuration()

DEVELOPER = config["DEVELOPER"]

developerHost = DEVELOPER["HOST"]
developerPort = DEVELOPER["PORT"]

import requests

from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import Conflict
from werkzeug.exceptions import Unauthorized
from werkzeug.exceptions import BadRequest

class Session_Model:
    def __init__(self) -> None:
        """
        """

    def authenticate(self, uid: str, user_agent: str, cookie: dict, verification_path: str) -> None:
        """
        """
        try:
            logger.debug("Authenticating developer session for %s ..." % uid)

            url = f"{developerHost}:{developerPort}/{verification_path}"
            data = {
                "uid": uid,
                "user_agent": user_agent,
                "cookie": cookie
            }

            res = requests.post(url=url, json=data)

            if res.status_code == 200:
                logger.info("- Successfully authenticated developer session")
            elif res.status_code == 400:
                logger.info("- Developer's API status code = %s" % res.status_code)
                raise BadRequest()
            elif res.status_code == 401:
                logger.info("- Developer's API status code = %s" % res.status_code)
                raise Unauthorized()
            elif res.status_code == 409:
                logger.info("- Developer's API status code = %s" % res.status_code)
                raise Conflict()
            else:
                logger.info("- Developer's API status code = %s" % res.status_code)
                raise InternalServerError()

        except BadRequest:
            raise BadRequest()
        except Unauthorized:
            raise Unauthorized()
        except Conflict:
            raise Conflict()
        except Exception as error:
            raise InternalServerError(error)

