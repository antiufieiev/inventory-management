from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Callable

from bot.database.model import CheeseVariants, database_proxy
from bot.localization.localization import localization_map, Keys
from bot.usecase.state_values import *


async def prepareSelectCheeseTypeUseCase(
        callback_filter: str,
        update: Update,
        button_name_mapper: Callable[[CheeseVariants], str] = lambda variant: variant.name,
        filter_func: Callable[[CheeseVariants], bool] = lambda variant: True
) -> int:
    with database_proxy.connection_context():
        variants = CheeseVariants.select()
        variants_filtered = filter(filter_func, variants)
        data = list(
            map(lambda variant: InlineKeyboardButton(
                text=button_name_mapper(variant),
                callback_data=f"{callback_filter}{STATE_CHEESE_TYPE_SELECTED}:{variant.name}"
            ), variants_filtered)
        )
        chunks = [data[x:x + 3] for x in range(0, len(data), 3)]
        reply_markup = InlineKeyboardMarkup(chunks)

        await update.effective_message.reply_text(
            text=localization_map[Keys.SELECT_CHEESE_TYPE],
            reply_markup=reply_markup
        )
        return STATE_WAIT_FOR_CHEESE_TYPE_SELECTION


async def onCheeseTypeSelected(cheese_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not cheese_type.strip():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=localization_map[Keys.ERROR_EMPTY])
        return STATE_WAIT_FOR_CHEESE_TYPE_SELECTION

    type_variant = CheeseVariants.select().where(CheeseVariants.name == cheese_type)
    if type_variant.count() != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ERROR_NO_TYPE_EXIST]
        )
        return STATE_WAIT_FOR_CHEESE_TYPE_SELECTION

    context.user_data["cheese_id"] = type_variant[0].id
    return STATUS_SUCCESS
