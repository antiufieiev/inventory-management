import time
import peewee

from playhouse.migrate import *


def connect_db(db, retries=3, delay=5):
    while True:
        retries -= 1
        try:
            db.connect()
        except OperationalError:
            if retries == 0:
                raise
            time.sleep(delay)
        else:
            return True


class ReconnectingProxy(Proxy):
    def connect(self):
        return connect_db(self.obj)


database_proxy = ReconnectingProxy()
database_version = 2


class BaseModel(Model):
    class Meta:
        database = database_proxy


class UserTable(BaseModel):
    class Meta:
        db_table = 'user'

    user_id = IntegerField(unique=True)
    access_level = IntegerField(default=0)
    username = CharField(default='')


class CheeseVariants(BaseModel):
    class Meta:
        db_table = 'cheese_variant'

    id = AutoField(unique=True)
    name = CharField(unique=True)


class Batches(BaseModel):
    class Meta:
        db_table = 'batch'
        primary_key = CompositeKey('cheese_id', 'batch_number', 'packed')

    batch_number = CharField(unique=True)
    cheese_id = ForeignKeyField(CheeseVariants, field='id', on_delete='CASCADE')
    count = FloatField()
    packed = BooleanField()
    comment = TextField()


class Logs(BaseModel):
    class Meta:
        db_table = "log"

    user_id = IntegerField()
    text = CharField()
    date = DateTimeField()


class DatabaseMetadata(BaseModel):
    class Meta:
        db_table = "db_metadata"

    version = IntegerField(primary_key=True)
