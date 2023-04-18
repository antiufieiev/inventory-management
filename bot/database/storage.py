import os

from bot.database.model import *


def initStorage():
    db = MySQLDatabase(
        database=os.environ["MYSQL_DATABASE"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"])
    )
    database_proxy.initialize(db)
    with database_proxy.connection_context():
        db.create_tables([UserTable, CheeseVariants, Batches, Logs], fail_silently=True)
