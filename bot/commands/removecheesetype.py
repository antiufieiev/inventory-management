from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.commands.basecommand import BaseConversation
from bot.commands.default_fallback import DefaultFallbackCommand
from bot.database.model import database_proxy
from bot.entity.entities import AccessLevel
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import localization_map, Keys
from bot.usecase import selectcheesetypeusecase, removecheesetypeusecase
from bot.usecase.state_values import *


class RemoveCheeseTypeCommand(BaseConversation):

    def __init__(self):
        super(RemoveCheeseTypeCommand, self).__init__(
            command_name="removecheesetype",
            fallback_command=DefaultFallbackCommand()
        )
        self.access_level = AccessLevel.ADMIN

    def createStatesWithHandlers(self):
        return {
            STATE_WAIT_FOR_CHEESE_TYPE_SELECTION: [CallbackQueryHandler(self.handleInlineButtonClick, pattern=f"^{self.callback_filter}")]
        }

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        with database_proxy.connection_context():
            if checkUserAccess(update) >= AccessLevel.ADMIN:
                return await selectcheesetypeusecase.prepareSelectCheeseTypeUseCase(self.callback_filter, update)
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
                return ConversationHandler.END

    async def handleInlineButtonClick(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        filtered = self.omitFilter(query.data).partition(':')
        state = filtered[0]
        data = filtered[2]
        new_state = ConversationHandler.END
        if state == str(STATE_CHEESE_TYPE_SELECTED):
            new_state = await self.handleCheeseTypeSelected(data, update, context)

        await query.answer()
        return new_state

    @staticmethod
    async def handleCheeseTypeSelected(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcheesetypeusecase.onCheeseTypeSelected(data, update, context)
        if result != STATUS_SUCCESS:
            return result

        await removecheesetypeusecase.removeCheeseTypeWithId(int(context.user_data["cheese_id"]), update, context)

        return ConversationHandler.END
