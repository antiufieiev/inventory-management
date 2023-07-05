from telegram import Update
from telegram.ext import ContextTypes

from bot.usecase.state_values import *
from bot.localization.localization import localization_map, Keys


def check_format(string):
    if string.replace(".", "").isnumeric():
        return True
    else:
        return False


async def prepareCountState(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization_map[Keys.ENTER_CHEESE_AMOUNT]
    )
    return STATE_WAIT_FOR_COUNT_INPUT


async def handleCountEntered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    count = update.message.text
    if check_format(count):
        context.user_data["count"] = count
        return STATUS_SUCCESS
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.COUNT_INPUT_ERROR_NUMERIC]
        )
        return STATE_WAIT_FOR_COUNT_INPUT
