import logging
logger = logging.getLogger(__name__)

from twilio.rest import Client

from werkzeug.exceptions import InternalServerError

class Twilio_Model:
    def __init__(self, account_sid: str, auth_token: str, service_sid: str = None, _from: str = None) -> None:
        """
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.service_sid = service_sid
        self._from = _from
        self.client = Client(self.account_sid, self.auth_token)

    def message(self, number:str, text: str) -> None:
        """
        """
        try:
            logger.debug("requesting twilio sms ...")

            if self.service_sid:
                message = self.client.messages \
                            .create(
                                messaging_service_sid=self.service_sid, 
                                body=text,      
                                to=number
                            )
            elif self._from:
                 message = self.client.messages \
                            .create(
                                from_=self._from, 
                                body=text,      
                                to=number
                            )

            logger.info("- Successfully requested twilio sms")

            return message

        except Exception as error:
            raise InternalServerError(error)