import peewee
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButtonRequestUser, KeyboardButton
from telegram.ext import MessageHandler, filters

from bot.commands.basecommand import *
from bot.commands.default_fallback import *
from bot.database.model import UserTable, database_proxy
from bot.feature.activitylogger import ActivityLogger
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class AddUserCommand(BaseConversation):
    STATE_USER_SELECTION, STATE_USER_SELECTED = range(2)

    def __init__(self):
        super(AddUserCommand, self).__init__(
            command_name="adduser",
            fallback_command=DefaultFallbackCommand()
        )
        self.access_level = AccessLevel.ADMIN

    def createStatesWithHandlers(self):
        return {
            self.STATE_USER_SELECTION: [MessageHandler(filters.StatusUpdate.USER_SHARED, self.handleUserSelection)],
            self.STATE_USER_SELECTED: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleAccessLevelSelection)]
        }

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if checkUserAccess(update) == AccessLevel.ADMIN:
            keyboard = [
                [KeyboardButton(localization_map[Keys.SELECT_USER], request_user=KeyboardButtonRequestUser(1))]
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

    async def handleUserSelection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.user_shared:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_BLANK_USERNAME]
            )
            return self.STATE_USER_SELECTION
        context.user_data["user_id"] = update.message.user_shared.user_id
        keyboard = [
            [
                localization_map[Keys.ACCESS_LEVEL_ADMIN],
                localization_map[Keys.ACCESS_LEVEL_EMPLOYEE],
                localization_map[Keys.ACCESS_LEVEL_MANAGER]
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.effective_message.reply_text(
            text=localization_map[Keys.SELECT_ACCESS_LEVEL],
            reply_markup=reply_markup
        )
        return self.STATE_USER_SELECTED

    async def handleAccessLevelSelection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = context.user_data["user_id"]
        if (update.message.text == localization_map[Keys.ACCESS_LEVEL_EMPLOYEE]
                or update.message.text == localization_map[Keys.ACCESS_LEVEL_ADMIN]
                or update.message.text == localization_map[Keys.ACCESS_LEVEL_MANAGER]):

            access_level = update.message.text
            access_level_int = -1

            if access_level == localization_map[Keys.ADMIN]:
                access_level_int = AccessLevel.ADMIN
            if access_level == localization_map[Keys.EMPLOYEE]:
                access_level_int = AccessLevel.EMPLOYEE
            if access_level == localization_map[Keys.ACCESS_LEVEL_MANAGER]:
                access_level_int = AccessLevel.MANAGER

            try:
                with database_proxy.connection_context():
                    UserTable(user_id=user_id, access_level=access_level_int).save()
                    context.user_data["access_level"] = access_level

                    input_text = localization_map[Keys.ADD_USER_SUCCESS].format(user_id, access_level)

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=input_text,
                        reply_markup=ReplyKeyboardRemove()
                    )
                    await self.logger.logActivity(input_text, update, context)
            except peewee.IntegrityError:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=localization_map[Keys.ERROR_ADD_USER],
                    reply_markup=ReplyKeyboardRemove()
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.USE_KEYBOARD_AS_INPUT_ERROR]
            )
            return self.STATE_USER_SELECTED
        context.user_data.clear()
        return ConversationHandler.END
