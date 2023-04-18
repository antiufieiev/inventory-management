from command.basecommand import *
from command.default_fallback import *
from database.model import Batches, database_proxy
from feature.permissionchecker import checkUserAccess
from localization.localization import *


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
                for batch in Batches.select():
                    line = localization_map[Keys.PRINT_DATABASE_STATE_LINE].format(
                        batch.cheese_id.name,
                        batch.batch_number,
                        str(batch.count),
                        batch.comment
                    )
                    if batch.packed == 1:
                        packed += line
                    if batch.packed == 0:
                        unpacked += line
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.PRINT_DATABASE_STATE].format(packed, unpacked)
            )
        else:
            await update.effective_message.reply_text(
                text=localization_map[Keys.ACCESS_DENIED],
            )
        return ConversationHandler.END
