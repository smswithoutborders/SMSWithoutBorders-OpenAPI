from asyncio.log import logger

import phonenumbers
from phonenumbers import geocoder
from phonenumbers import carrier
from phonenumbers import NumberParseException
from phonenumbers import format_number

class InvalidPhoneNUmber(Exception):
    def __init__(self, message="Invalid phone number"):
        self.message = message
        super().__init__(self.message)

class InvalidCountryCode(Exception):
    def __init__(self, message="Invalid country code"):
        self.message = message
        super().__init__(self.message)

class MissingCountryCode(Exception):
    def __init__(self, message="Missing country code"):
        self.message = message
        super().__init__(self.message)

class NotE164PhoneNumberFormat(Exception):
    def __init__(self, message="Phone number is not E164 Format"):
        self.message = message
        super().__init__(self.message)

def get_phonenumber_carrier_name(MSISDN: str) -> str:
    """Returns the carrier name of MSISDN.
    Args:
        MSISDN (str):
            The phone number for which carrier name is required.

    Returns:
        (str): carrier name

    Exceptions:
        INVALID_PHONE_NUMBER_EXCEPTION
        INVALID_COUNTRY_CODE_EXCEPTION
        MISSING_COUNTRY_CODE_EXCEPTION
    """

    try:
        _number = phonenumbers.parse(MSISDN, "en")

        if not phonenumbers.is_valid_number(_number):
            raise InvalidPhoneNUmber()

        return phonenumbers.carrier.name_for_number(_number, "en")

    except phonenumbers.NumberParseException as error:
        if error.error_type == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE:
            if MSISDN[0] == "+" or MSISDN[0] == "0":
                raise InvalidCountryCode()
            else:
                raise MissingCountryCode()
        else:
            raise error

    except Exception as error:
        raise error

def get_phonenumber_country(MSISDN: str) -> str:
    """Returns the country of MSISDN.
    Args:
        MSISDN (str):
            The phone number for which country is required.

    Returns:
        (str): country name

    Exceptions:
        INVALID_PHONE_NUMBER_EXCEPTION
        INVALID_COUNTRY_CODE_EXCEPTION
        MISSING_COUNTRY_CODE_EXCEPTION
    """

    try:
        _number = phonenumbers.parse(MSISDN, "en")

        if not phonenumbers.is_valid_number(_number):
            raise InvalidPhoneNUmber()

        country_name = geocoder.country_name_for_number(_number, "en")

        return country_name

    except phonenumbers.NumberParseException as error:
        if error.error_type == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE:
            if MSISDN[0] == "+" or MSISDN[0] == "0":
                raise InvalidCountryCode()
            else:
                raise MissingCountryCode()
        else:
            raise error

    except Exception as error:
        raise error

def check_phonenumber_E164(MSISDN: str) -> bool:
    """
    """
    try:
        _number = phonenumbers.parse(MSISDN, "en")

        if MSISDN != phonenumbers.format_number(_number, phonenumbers.PhoneNumberFormat.E164):
            raise NotE164PhoneNumberFormat()
        else:
            return True

    except Exception as error:
        logger.exception(error)
        raise NotE164PhoneNumberFormat()
