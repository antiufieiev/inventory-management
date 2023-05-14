import peewee

from bot.commands.default_fallback import *
from bot.database.model import Batches, database_proxy
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class DatabaseStateCommand(BaseConversation):

    def __init__(self):
        super(DatabaseStateCommand, self).__init__(
            command_name="databasestate",
            fallback_command=DefaultFallbackCommand()
        )

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        with database_proxy.connection_context():
            if checkUserAccess(update) == AccessLevel.ADMIN:
                packed = ''
                unpacked = ''
                packed_batches = Batches.select(Batches, peewee.fn.SUM(Batches.count).alias('sum')) \
                    .where(Batches.packaging.is_null(False)) \
                    .group_by(Batches.cheese, Batches.packaging)
                unpacked_batches = Batches.select().where(Batches.packaging.is_null())
                for batch in packed_batches:
                    packed += localization_map[Keys.PRINT_DATABASE_STATE_LINE_PACKED].format(
                        batch.cheese.name,
                        batch.packaging.packaging,
                        str(batch.sum)
                    )

                for batch in unpacked_batches:
                    unpacked += localization_map[Keys.PRINT_DATABASE_STATE_LINE].format(
                        batch.cheese.name,
                        batch.batch_number,
                        str(batch.count),
                        batch.comment
                    )

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=localization_map[Keys.PRINT_DATABASE_STATE].format(packed, unpacked)
                )
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
        context.user_data.clear()
        return ConversationHandler.END
