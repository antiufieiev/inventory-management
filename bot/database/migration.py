from bot.database.model import *
from bot.entity.entities import AccessLevel
from playhouse.migrate import *


class Migrator:
    migrator = MySQLMigrator(database_proxy)

    def migrate(self):
        with database_proxy.connection_context():
            current_version = 0
            try:
                current_version = DatabaseMetadata.get().version
            except peewee.DoesNotExist:
                pass
            self.executeMigration(current_version, database_version)

    def executeMigration(self, from_version: int, to_version: int):
        if from_version == to_version:
            return
        if from_version == 0:
            self.from_0_To_1_Migration()

        with database_proxy.atomic():
            DatabaseMetadata.delete().execute()
            DatabaseMetadata(version=from_version + 1).save(force_insert=True)

        self.executeMigration(from_version + 1, to_version)

    def from_0_To_1_Migration(self):
        with database_proxy.atomic():
            database_proxy.create_tables([DatabaseMetadata], fail_silently=True)
            UserTable.update({UserTable.access_level: AccessLevel.ADMIN})\
                .where(UserTable.access_level == 2)\
                .execute()
            migrate(
                self.migrator.add_column('user', 'username', CharField(default=''))
            )
