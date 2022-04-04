
import phonenumbers
from phonenumbers import geocoder, carrier

INVALID_PHONE_NUMBER_EXCEPTION = "INVALID PHONE NUMBER"
INVALID_COUNTRY_CODE_EXCEPTION = "INVALID COUNTRY CODE"
MISSING_COUNTRY_CODE_EXCEPTION = "MISSING COUNTRY CODE"

def get_phonenumber_country(MSISDN:str)->str:
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
        _number = phonenumbers.parse(MSISDN, 'en')

        if not phonenumbers.is_valid_number(_number):
            return Exception(INVALID_PHONE_NUMBER_EXCEPTION)

        return \
                phonenumbers.carrier.name_for_number(_number, 'en')

    except phonenumbers.NumberParseException as error:
        if error.error_type == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE:
            if MSISDN[0] == '+' or MSISDN[0] == '0':
                raise Exception(INVALID_COUNTRY_CODE_EXCEPTION)
            else:
                raise Exception(MISSING_COUNTRY_CODE_EXCEPTION)

        else:
            raise error

    except Exception as error:
        raise error
