import peewee
from telegram.ext import MessageHandler, filters

from bot.commands.default_fallback import *
from bot.database.model import database_proxy
from bot.database.storage import CheeseVariants
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class AddCheeseCommand(BaseConversation):
    STATE_INPUT_TYPE = 1

    def __init__(self):
        super(AddCheeseCommand, self).__init__(
            command_name="addcheesetype",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            self.STATE_INPUT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCheeseTypeEntered)],
        }

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        with database_proxy.connection_context():
            if checkUserAccess(update) >= AccessLevel.EMPLOYEE:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=localization_map[Keys.ENTER_CHEESE_NAME])
                return self.STATE_INPUT_TYPE
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
                return ConversationHandler.END

    async def handleCheeseTypeEntered(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        type_name = update.message.text
        if not type_name.strip():
            await context.bot.send_message(chat_id=update.effective_chat.id, text=localization_map[Keys.ERROR_EMPTY])
            return self.STATE_INPUT_TYPE

        try:
            with database_proxy.connection_context():
                CheeseVariants(name=type_name).save()

                input_text = localization_map[Keys.CHEESE_TYPE_ADDED].format(type_name)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=input_text
                )

                await self.logger.logActivity(input_text, update, context)
        except peewee.IntegrityError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_CHEESE_TYPE_EXIST]
            )
        context.user_data.clear()
        return ConversationHandler.END
