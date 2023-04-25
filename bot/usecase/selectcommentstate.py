from telegram import Update
from telegram.ext import ContextTypes

from bot.usecase.state_values import *
from bot.localization.localization import localization_map, Keys


async def prepareSelectCommentState(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization_map[Keys.ENTER_COMMENT]
    )
    return STATE_WAIT_FOR_COMMENT_INPUT


async def handleCommentSelected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.strip():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ERROR_EMPTY]
        )
        return STATE_WAIT_FOR_COMMENT_INPUT

    comment = update.message.text
    context.user_data["comment"] = comment
    return STATUS_SUCCESS
