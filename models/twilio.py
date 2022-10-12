import logging
logger = logging.getLogger(__name__)

from config_init import configuration

config = configuration()
twilio = config["TWILIO"]

from twilio.rest import Client

account_sid = twilio["ACCOUNT_SID"]
auth_token = twilio["AUTH_TOKEN"]
service_sid = twilio["SERVICE_SID"]

from werkzeug.exceptions import InternalServerError

class Twilio_Model:
    def __init__(self) -> None:
        """
        """
        self.client = Client(account_sid, auth_token)

    def message(self, number:str, text: str) -> None:
        """
        """
        try:
            logger.debug("requesting twilio sms ...")

            message = self.client.messages \
                        .create(
                            messaging_service_sid=service_sid, 
                            body=text,      
                            to=number
                        )

            logger.info("- Successfully requested twilio sms")

            return message

        except Exception as error:
            raise InternalServerError(error)