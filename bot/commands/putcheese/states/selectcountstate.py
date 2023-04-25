from telegram import Update
from telegram.ext import ContextTypes

from bot.commands.putcheese.states.state_values import *
from bot.localization.localization import localization_map, Keys


async def prepareCountState(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization_map[Keys.ENTER_CHEESE_AMOUNT]
    )
    return STATE_WAIT_FOR_COUNT_INPUT


def handleCountEntered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = update.message.text
    context.user_data["count"] = count
