from config_init import configuration
config = configuration()
database = config["DATABASE"]

from peewee import MySQLDatabase
from peewee import Model
from peewee import DatabaseError

try:
    db = MySQLDatabase(
        database["MYSQL_DATABASE"],
        user=database["MYSQL_USER"],
        password=database["MYSQL_PASSWORD"],
        host=database["MYSQL_HOST"],
    )

except DatabaseError as err:
    raise err

class BaseModel(Model):
    """
    Users database model.
    """
    class Meta:
        database = db
