from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database.model import database_proxy, Batches
from bot.localization.localization import localization_map, Keys
from bot.usecase.state_values import *


async def prepareSelectBatch(callback_filter: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with database_proxy.connection_context():
        cheese_id = int(context.user_data["cheese_id"])
        query = Batches.select().where(Batches.cheese == cheese_id).execute()

        data = list(map(lambda batch: InlineKeyboardButton(
            f"{batch.batch_number}-{batch.count}",
            callback_data=f"{callback_filter}{STATE_BATCH_SELECTED}:{batch.batch_number}"
        ), query))
        chunks = [data[x:x + 3] for x in range(0, len(data), 3)]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=chunks)

        await update.effective_message.reply_text(
            text=localization_map[Keys.SELECT_CHEESE_BATCH],
            reply_markup=reply_markup
        )
        return STATE_WAIT_FOR_BATCH_SELECTION


async def onBatchSelected(selected_batch: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not selected_batch.strip():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ERROR_EMPTY]
        )
        return STATE_WAIT_FOR_BATCH_SELECTION

    context.user_data["batch_number"] = selected_batch
    return STATUS_SUCCESS
