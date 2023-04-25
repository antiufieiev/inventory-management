from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.commands.putcheese.states.state_values import *
from bot.database.model import database_proxy, Packaging
from bot.localization.localization import localization_map, Keys


async def preparePackagingState(callback_filter: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with database_proxy.connection_context():
        packagingList = Packaging.select().execute()
        data = list(
            map(lambda packaging: InlineKeyboardButton(
                text=str(packaging.packaging),
                callback_data=f"{callback_filter}{STATE_WAIT_FOR_PACKAGING_SELECTION}:{packaging.id}"
            ), packagingList)
        )
        keyboard = [data]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ENTER_PACKAGING],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return STATE_WAIT_FOR_PACKAGING_SELECTION


def handlePackagingFormatSelected(packaging_id: str, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["packaging_id"] = packaging_id
