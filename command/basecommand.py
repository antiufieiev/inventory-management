from typing import Any

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, BaseHandler, CallbackContext

from entity.entities import AccessLevel


class BaseCommand(object):

    def __int__(self, command_name: str):
        self.command_name = command_name
        self.callback_filter = command_name
        self.access_level = AccessLevel.EMPLOYEE

    def createTelegramCommand(self) -> CommandHandler:
        return CommandHandler(self.command_name, self.executeCommand)

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return ConversationHandler.END

    def omitFilter(self, data: str) -> str:
        return data.removeprefix(self.callback_filter)


class BaseConversation(BaseCommand):

    def __init__(self, command_name: str, fallback_command: BaseCommand):
        self.command_name = command_name
        self.callback_filter = command_name
        self.fallback_command = fallback_command

    def createTelegramCommand(self) -> CommandHandler:
        return CommandHandler(self.command_name, self.executeCommand)

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return ConversationHandler.END

    def createTelegramConversation(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[self.createTelegramCommand()],
            states=self.createStatesWithHandlers(),
            fallbacks=[self.fallback_command.createTelegramCommand()],
        )

    def createStatesWithHandlers(self) -> dict[object, list[BaseHandler[Update, CallbackContext[Any, Any, Any, Any]]]]:
        return {}
