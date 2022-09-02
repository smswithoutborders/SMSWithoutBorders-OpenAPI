import logging
logger = logging.getLogger(__name__)

from config_init import configuration

config = configuration()
database = config["DATABASE"]

from contextlib import closing
from mysql.connector import connect
from mysql.connector import Error

from schemas.baseModel import db
from schemas.metrics import Metrics

from werkzeug.exceptions import InternalServerError

def create_database() -> None:
    """
    Create all databases.

    Arguments:
        None

    Returns:
        None
    """
    try:
        with closing(
            connect(
                user=database["MYSQL_USER"],
                password=database["MYSQL_PASSWORD"],
                host=database["MYSQL_HOST"],
                auth_plugin="mysql_native_password",
            )
        ) as connection:
            create_db_query = ("CREATE DATABASE IF NOT EXISTS %s;" % database["MYSQL_DATABASE"])
            with closing(connection.cursor()) as cursor:
                logger.debug("Creating database %s ..." % database["MYSQL_DATABASE"])
                cursor.execute(create_db_query)
                logger.info("- Database %s successfully created" % database["MYSQL_DATABASE"])

    except Error as error:
        raise InternalServerError(error)
        
    except Exception as error:
        raise InternalServerError(error)


def create_tables() -> None:
    """
    Create all database tables.

    Arguments:
        None

    Returns:
        None
    """
    try:
        # create users database tables
        logger.debug("Syncing database %s ..." % database["MYSQL_DATABASE"])
        db.create_tables([Metrics])

        logger.info("- Successfully Sync database %s" % database["MYSQL_DATABASE"])

    except Exception as error:
        raise InternalServerError(error)