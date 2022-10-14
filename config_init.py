import os
from configparser import ConfigParser

def configuration() -> dict:
    """
    """
    config_filepath = os.path.join(os.path.dirname(__file__), 'config', 'default.ini')

    if not os.path.exists(config_filepath):
        error = "Configurations file not found at '%s'" % config_filepath
        raise FileNotFoundError(error)

    config = ConfigParser()
    config.read(config_filepath)

    setup_filepath = os.path.join(os.path.dirname(__file__), 'config', 'setup.ini')

    if not os.path.exists(setup_filepath):
        error = "Setup file not found at '%s'" % setup_filepath
        raise FileNotFoundError(error)

    setup = ConfigParser()
    setup.read(setup_filepath)

    return {
        "DATABASE": config["DATABASE"],
        "API": config["API"],
        "SSL_API": config["SSL_API"],
        "SETUP_CREDS": setup["CREDENTIALS"],
        "DEVELOPER": config["DEVELOPER"]
    }
