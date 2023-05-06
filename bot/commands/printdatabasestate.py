from bot.commands.basecommand import *
from bot.commands.default_fallback import *
from bot.database.model import Batches, Packaging, database_proxy
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class DatabaseStateCommand(BaseConversation):

    def __init__(self):
        super(DatabaseStateCommand, self).__init__(
            command_name="databasestate",
            fallback_command=DefaultFallbackCommand()
        )

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if checkUserAccess(update) == AccessLevel.ADMIN:
            packed = ''
            unpacked = ''
            with database_proxy.connection_context():
                for batch in Batches.select(Batches):
                    if batch.packaging is not None:
                        line = localization_map[Keys.PRINT_DATABASE_STATE_LINE_PACKED].format(
                            batch.cheese.name,
                            batch.packaging.packaging,
                            str(batch.count),
                            batch.comment

                        )
                        packed += line
                    if batch.packaging is None:
                        line_unpacked = localization_map[Keys.PRINT_DATABASE_STATE_LINE].format(
                            batch.cheese.name,
                            batch.batch_number,
                            str(batch.count),
                            batch.comment
                        )
                        unpacked += line_unpacked

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
