from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.commands.putcheese.states.state_values import *
from bot.localization.localization import localization_map, Keys


async def prepareIsPackagedState(callback_filter: str, update: Update) -> int:
    keyboard = [
        [
            InlineKeyboardButton(
                text=localization_map[Keys.CHEESE_PACKED],
                callback_data=f"{callback_filter}{STATE_WAIT_FOR_IS_PACKED_SELECTION}:{localization_map[Keys.CHEESE_PACKED]}"
            ),
            InlineKeyboardButton(
                text=localization_map[Keys.CHEESE_UNPACKED],
                callback_data=f"{callback_filter}{STATE_WAIT_FOR_IS_PACKED_SELECTION}:{localization_map[Keys.CHEESE_UNPACKED]}"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.reply_text(
        text=localization_map[Keys.CHEESE_PACKED_STATE],
        reply_markup=reply_markup
    )
    return STATE_WAIT_FOR_IS_PACKED_SELECTION


async def onIsPackagedStateSelected(packed_state: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not packed_state.strip():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ERROR_EMPTY]
        )
        return STATE_WAIT_FOR_IS_PACKED_SELECTION

    is_packed = None
    if packed_state == localization_map[Keys.CHEESE_PACKED]:
        is_packed = True
    if packed_state == localization_map[Keys.CHEESE_UNPACKED]:
        is_packed = False
    if is_packed is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ERROR_EMPTY]
        )
        return STATE_WAIT_FOR_IS_PACKED_SELECTION
    context.user_data["is_packed"] = is_packed
    return STATUS_SUCCESS
