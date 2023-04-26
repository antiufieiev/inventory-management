from bot.commands.basecommand import *


class DefaultFallbackCommand(BaseCommand):

    def __init__(self):
        super(DefaultFallbackCommand, self).__int__(command_name="cancel")

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
        return ConversationHandler.END
