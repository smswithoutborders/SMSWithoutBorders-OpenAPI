import os
from configparser import ConfigParser


def configuration():
    config = ConfigParser()
    config_filepath = os.path.join(os.path.dirname(__file__), "config", "default.ini")
    config.read(config_filepath)

    setup = ConfigParser()
    setup_filepath = os.path.join(os.path.dirname(__file__), "setup.ini")
    setup.read(setup_filepath)

    return {
        "API": config["API"],
        "SSL_API": config["SSL_API"],
        "SETUP_CREDS": setup["CREDENTIALS"],
        "DEVELOPER": config["DEVELOPER"],
    }
