from datetime import datetime
from peewee import Model, CharField, TextField, DateTimeField

from src.schemas.db_connector import db

class Metrics(Model):
    uid = CharField(primary_key=True)
    phone_number = CharField(null=True)
    operator_name = CharField(null=True)
    status = CharField(null=True)
    message = TextField(null=True)
    auth_id = CharField(null=True)
    createdAt = DateTimeField(null=True, default=datetime.now)

    class Meta:
        database = db

if db.table_exists('metrics') is False:
    db.create_tables([Metrics])