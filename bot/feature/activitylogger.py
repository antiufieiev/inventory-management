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

    def __init__(self, command_name):
        self.command_name = command_name

    async def logActivity(self, text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_message.text.strip():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )

        try:
            Logs(
                user_id=update.effective_user.id,
                text=localization_map[Keys.COMMAND_LOG_SUCCESS].format(text, self.command_name),
                date=getCurrentTime()
            ).save()

        except peewee.IntegrityError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_LOG_INSERT]
            )
