from telegram import Update
from telegram.ext import ContextTypes

from bot.database.model import database_proxy, CheeseVariants
from bot.localization.localization import Keys, localization_map


async def removeCheeseTypeWithId(type_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    with database_proxy.connection_context():
        variant = CheeseVariants.get(CheeseVariants.id == type_id)
        CheeseVariants.delete().where(CheeseVariants.id == type_id).execute()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.CHEESE_VARIANT_DELETED].format(variant.name)
        )
