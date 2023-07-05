from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, KeyboardButtonRequestUser
from telegram.ext import MessageHandler, filters

from bot.commands.basecommand import *
from bot.commands.default_fallback import *
from bot.database.model import Logs, database_proxy
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class UserHistoryCommand(BaseConversation):
    STATE_NICKNAME_SELECTED = 1

    def __init__(self):
        super(UserHistoryCommand, self).__init__(
            command_name="userhistory",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            self.STATE_NICKNAME_SELECTED: [
                MessageHandler(filters.StatusUpdate.USER_SHARED, self.handleNicknameSelected)
            ]
        }

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        with database_proxy.connection_context():
            if checkUserAccess(update) == AccessLevel.ADMIN:
                keyboard = [
                    [KeyboardButton(localization_map[Keys.SELECT_USER], request_user=KeyboardButtonRequestUser(1))]
                ]
                await update.effective_message.reply_text(
                    text=localization_map[Keys.SELECT_USER],
                    reply_markup=ReplyKeyboardMarkup(keyboard)
                )
                return self.STATE_NICKNAME_SELECTED
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
                return ConversationHandler.END

    @staticmethod
    async def handleNicknameSelected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.user_shared:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )

        user_id = update.message.user_shared.user_id
        with database_proxy.connection_context():
            query = Logs().select().where(Logs.user_id == user_id).order_by(Logs.date.asc()).limit(50)

            for log in query:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=localization_map[Keys.PRINT_LOG].format(str(log.user_id), log.text, str(log.date)),
                    reply_markup=ReplyKeyboardRemove()
                )
        context.user_data.clear()
        return ConversationHandler.END
