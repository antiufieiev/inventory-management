from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestUser, ReplyKeyboardRemove

from bot.commands.basecommand import BaseConversation
from bot.commands.default_fallback import DefaultFallbackCommand
from bot.database.model import database_proxy, UserTable
from bot.entity.entities import AccessLevel
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import localization_map, Keys


class RemoveUserCommand(BaseConversation):
    STATE_USER_SELECTION, STATE_USER_SELECTED = range(2)
    REMOVE_USER_REQUEST_CODE = 10

    def __init__(self):
        super(RemoveUserCommand, self).__init__(
            command_name="removeuser",
            fallback_command=DefaultFallbackCommand()
        )
        self.access_level = AccessLevel.ADMIN

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        with database_proxy.connection_context():
            if checkUserAccess(update) == AccessLevel.ADMIN:
                keyboard = [
                    [
                        KeyboardButton(
                            localization_map[Keys.SELECT_USER],
                            request_user=KeyboardButtonRequestUser(request_id=self.REMOVE_USER_REQUEST_CODE)
                        )
                    ]
                ]
                await update.effective_message.reply_text(
                    text=localization_map[Keys.SELECT_USER],
                    reply_markup=ReplyKeyboardMarkup(keyboard)
                )
                return self.STATE_USER_SELECTION
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
                return ConversationHandler.END

    def createStatesWithHandlers(self):
        return {
            self.STATE_USER_SELECTION: [MessageHandler(filters.StatusUpdate.USER_SHARED, self.handleUserSelection)]
        }

    async def handleUserSelection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.user_shared.request_id != self.REMOVE_USER_REQUEST_CODE:
            return self.STATE_USER_SELECTION
        if not update.message.user_shared:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_BLANK_USERNAME]
            )
            return self.STATE_USER_SELECTION
        user_id = update.message.user_shared.user_id

        with database_proxy.connection_context():
            UserTable.delete().where(UserTable.user_id == user_id).execute()

        await update.effective_message.reply_text(
            text=localization_map[Keys.USER_DELETED].format(user_id),
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
