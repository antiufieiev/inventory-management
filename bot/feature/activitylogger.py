from datetime import datetime

import peewee
import pytz

from bot.commands.basecommand import *
from bot.database.model import Logs
from bot.localization.localization import *


def getCurrentTime():
    european = pytz.timezone('Europe/Kyiv')
    date = datetime.now(european)
    return date


class ActivityLogger(object):

    def __init__(self, command_name, user_id, input_text: str):
        self.command_name = command_name
        self.user_id = user_id
        self.input_text = input_text

    async def logActivity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_message.text.strip():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )

        try:
            Logs(
                user_id=self.user_id,
                text=localization_map[Keys.COMMAND_LOG_SUCCESS].format(self.input_text, self.command_name),
                date=getCurrentTime()
            ).save()

        except peewee.IntegrityError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_LOG_INSERT]
            )
