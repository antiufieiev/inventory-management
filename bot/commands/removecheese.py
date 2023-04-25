import re

import peewee
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, filters, CallbackQueryHandler

from bot.commands.basecommand import *
from bot.commands.default_fallback import *
from bot.database.model import database_proxy
from bot.database.storage import CheeseVariants, Batches
from bot.feature.activitylogger import ActivityLogger
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *

pattern = "-" + ".*"


class RemoveCheeseCommand(BaseConversation):
    STATE_INIT, STATE_TYPE_SELECTED, STATE_PACKED_SELECTED, STATE_BATCH_SELECTED, STATE_COUNT_SELECTED = range(5)
    ADMIN, EMPLOYEE = range(2)

    def __init__(self):
        super(RemoveCheeseCommand, self).__init__(
            command_name="removecheese",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            self.STATE_TYPE_SELECTED: [CallbackQueryHandler
                                       (self.handleInlineButtonClick,
                                        pattern=f"^{self.callback_filter}")],
            self.STATE_PACKED_SELECTED: [CallbackQueryHandler
                                         (self.handleInlineButtonClick,
                                          pattern=f"^{self.callback_filter}")],
            self.STATE_COUNT_SELECTED: [MessageHandler
                                        (filters.TEXT & ~filters.COMMAND,
                                         self.handleCountSelected)],
            self.STATE_BATCH_SELECTED: [CallbackQueryHandler
                                        (self.handleInlineButtonClick,
                                         pattern=f"^{self.callback_filter}")]
        }

    async def handleInlineButtonClick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        filtered = self.omitFilter(query.data).partition(':')
        state = filtered[0]
        data = filtered[2]
        new_state = self.STATE_TYPE_SELECTED
        if state == str(self.STATE_INIT):
            new_state = await self.handleTypeSelectedAskPacked(data, update, context)
        if state == str(self.STATE_PACKED_SELECTED):
            new_state = await self.handlePackedEnteredAskBatch(data, update, context)
        if state == str(self.STATE_BATCH_SELECTED):
            new_state = await self.handleBatchSelectedAskCount(data, update, context)

        await query.answer()
        return new_state

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if checkUserAccess(update) >= AccessLevel.EMPLOYEE:
            query = Batches.select(Batches, peewee.fn.sum(Batches.count).alias("sum")).group_by(Batches.cheese_id)

            variants_and_counts = []

            for element in query:
                variants_and_counts.append(element.cheese_id.name + "-" + str(element.sum))

            data = list(map(lambda variant:
                            InlineKeyboardButton(variant, callback_data=f"{self.callback_filter}"
                                                                        f"{self.STATE_INIT}:{re.sub(pattern, '', variant)}"),
                            variants_and_counts))
            chunks = [data[x:x + 3] for x in range(0, len(data), 3)]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=chunks)

            await update.effective_message.reply_text(
                text=localization_map[Keys.SELECT_CHEESE_TYPE],
                reply_markup=reply_markup
            )

            return self.STATE_TYPE_SELECTED
        else:
            await update.effective_message.reply_text(
                text=localization_map[Keys.ACCESS_DENIED],
            )
            return ConversationHandler.END

    async def handleTypeSelectedAskPacked(self, cheese_type: str, update: Update,
                                          context: ContextTypes.DEFAULT_TYPE) -> int:
        type_variant = CheeseVariants.select().where(CheeseVariants.name == cheese_type)
        if type_variant.count() != 1:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_NO_TYPE_EXIST]
            )
            return self.STATE_TYPE_SELECTED

        context.user_data["cheese_id"] = type_variant[0].id
        context.user_data["cheese_type"] = cheese_type

        keyboard = [
            [
                InlineKeyboardButton(
                    text=localization_map[Keys.CHEESE_PACKED],
                    callback_data=f"{self.callback_filter}{self.STATE_PACKED_SELECTED}:{localization_map[Keys.CHEESE_PACKED]}"
                ),
                InlineKeyboardButton(
                    text=localization_map[Keys.CHEESE_UNPACKED],
                    callback_data=f"{self.callback_filter}{self.STATE_PACKED_SELECTED}:{localization_map[Keys.CHEESE_UNPACKED]}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            text=localization_map[Keys.CHEESE_PACKED_STATE],
            reply_markup=reply_markup
        )

        return self.STATE_PACKED_SELECTED

    async def handlePackedEnteredAskBatch(self, packed_state: str, update: Update,
                                          context: ContextTypes.DEFAULT_TYPE) -> int:
        if not packed_state.strip():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )
            return self.STATE_PACKED_SELECTED

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
            return self.STATE_PACKED_SELECTED
        print(is_packed)
        query = Batches.select().where((Batches.cheese_id == context.user_data["cheese_id"])
                                       & (Batches.packed == is_packed))
        pattern_batch = '/' + ".*"
        batches_and_counts = []
        for batch in query:
            batches_and_counts.append(batch.batch_number + "/" + str(batch.count))

        print(batches_and_counts)
        data = list(map(lambda variant:
                        InlineKeyboardButton(variant, callback_data=f"{self.callback_filter}"
                                                                    f"{self.STATE_BATCH_SELECTED}:"
                                                                    f"{re.sub(pattern_batch, '', variant)}"),
                        batches_and_counts))
        chunks = [data[x:x + 3] for x in range(0, len(data), 3)]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=chunks)

        await update.effective_message.reply_text(
            text=localization_map[Keys.ENTER_CHEESE_BATCH],
            reply_markup=reply_markup
        )

        return self.STATE_PACKED_SELECTED

    async def handleBatchSelectedAskCount(self, selected_batch: str, update: Update,
                                          context: ContextTypes.DEFAULT_TYPE) -> int:
        # batch_number = update.message.text
        # context.user_data["batch_number"] = batch_number
        if not selected_batch.strip():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )
            return self.STATE_BATCH_SELECTED

        context.user_data["batch_number"] = selected_batch

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ENTER_CHEESE_AMOUNT]
        )

        return self.STATE_COUNT_SELECTED

    async def handleCountSelected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        count = update.message.text
        context.user_data["count"] = count
        if count.isnumeric():
            with database_proxy.connection_context():
                query = Batches.select().where(
                    (Batches.cheese_id == context.user_data["cheese_id"]) &
                    (Batches.batch_number == context.user_data["batch_number"])
                )
                for batch in query:
                    if batch.count == float(count):
                        delete_ = Batches.delete().where(
                            (Batches.cheese_id == context.user_data["cheese_id"]) &
                            (Batches.batch_number == context.user_data["batch_number"])
                        )
                        delete_.execute()
                    if batch.count > float(count):
                        batch.count = batch.count - float(count)
                        batch.save()
                    if batch.count < float(count):
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=localization_map[Keys.COUNT_INPUT_ERROR_OVERLOAD]
                        )
                        return self.STATE_COUNT_SELECTED

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.COUNT_INPUT_ERROR_NUMERIC]
            )
            return self.STATE_COUNT_SELECTED

        input_text = localization_map[Keys.CHEESE_DELETE_SUCCESS].format(
            count,
            context.user_data["cheese_type"],
            context.user_data["batch_number"]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=input_text
        )
        with database_proxy.connection_context():
            active = ActivityLogger(self.command_name, update.effective_user.id, input_text)
            await active.logActivity(update, context)

        return ConversationHandler.END
