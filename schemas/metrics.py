from peewee import CharField
from peewee import TextField
from peewee import DateTimeField

from schemas.baseModel import BaseModel

from datetime import datetime

class Metrics(BaseModel):
    uid = CharField(primary_key=True)
    phone_number = CharField(null=True)
    operator_name = CharField(null=True)
    status = CharField(null=True)
    message = TextField(null=True)
    auth_id = CharField(null=True)
    createdAt = DateTimeField(null=True, default=datetime.now)