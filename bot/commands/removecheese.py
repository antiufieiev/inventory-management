import peewee
from telegram.ext import MessageHandler, filters, CallbackQueryHandler

from bot.commands.default_fallback import *
from bot.database.model import database_proxy
from bot.database.storage import Batches
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *
from bot.usecase import selectcheesetypeusecase, selectcountstate, selectbatchesusecase
from bot.usecase.state_values import *


class RemoveCheeseCommand(BaseConversation):

    def __init__(self):
        super(RemoveCheeseCommand, self).__init__(
            command_name="removecheese",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            STATE_WAIT_FOR_CHEESE_TYPE_SELECTION: [
                CallbackQueryHandler(self.handleInlineButtonClick, pattern=f"^{self.callback_filter}")
            ],
            STATE_WAIT_FOR_COUNT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCountSelected)
            ],
            STATE_WAIT_FOR_BATCH_SELECTION: [
                CallbackQueryHandler(self.handleInlineButtonClick, pattern=f"^{self.callback_filter}")
            ]
        }

    async def handleInlineButtonClick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        filtered = self.omitFilter(query.data).partition(':')
        state = filtered[0]
        data = filtered[2]
        new_state = ConversationHandler.END
        if state == str(STATE_CHEESE_TYPE_SELECTED):
            new_state = await self.handleTypeSelectedAskBatch(data, update, context)
        if state == str(STATE_BATCH_SELECTED):
            new_state = await self.handleBatchSelectedAskCount(data, update, context)

        await query.answer()
        return new_state

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if checkUserAccess(update) >= AccessLevel.EMPLOYEE:
            with database_proxy.connection_context():
                query_result = Batches.select(Batches, peewee.fn.sum(Batches.count).alias("sum"))\
                    .group_by(Batches.cheese).execute()
                return await selectcheesetypeusecase.prepareSelectCheeseTypeUseCase(
                    self.callback_filter,
                    update,
                    lambda variant: f"{variant.name}-{next(i for i in query_result if i.cheese == variant).sum}",
                    lambda variant: any(item.cheese == variant for item in query_result)
                )
        else:
            await update.effective_message.reply_text(
                text=localization_map[Keys.ACCESS_DENIED],
            )
            return ConversationHandler.END

    async def handleTypeSelectedAskBatch(self, cheese_type: str, update: Update,
                                         context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcheesetypeusecase.onCheeseTypeSelected(cheese_type, update, context)
        if result != STATUS_SUCCESS:
            return result

        context.user_data["cheese_type"] = cheese_type
        return await selectbatchesusecase.prepareSelectBatch(self.callback_filter, update, context)

    @staticmethod
    async def handleBatchSelectedAskCount(selected_batch: str, update: Update,
                                          context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectbatchesusecase.onBatchSelected(selected_batch, update, context)
        if result != STATUS_SUCCESS:
            return result

        return await selectcountstate.prepareCountState(update, context)

    async def handleCountSelected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcountstate.handleCountEntered(update, context)
        if result != STATUS_SUCCESS:
            return result
        await self.finalize(update, context)

    async def finalize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        count = float(context.user_data["count"])
        cheese_id = int(context.user_data["cheese_id"])
        batch_number = str(context.user_data["batch_number"])
        cheese_type = str(context.user_data["cheese_type"])
        with database_proxy.connection_context():
            batch = Batches.get(
                Batches.cheese == cheese_id and
                Batches.batch_number == batch_number
            )
            if batch.count == count:
                Batches.delete().where(
                    Batches.cheese == cheese_id and
                    Batches.batch_number == batch_number
                ).execute()
            if batch.count > count:
                batch.count = batch.count - count
                batch.save()
            if batch.count < count:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=localization_map[Keys.COUNT_INPUT_ERROR_OVERLOAD]
                )
                return STATE_WAIT_FOR_COUNT_INPUT

            success_text = localization_map[Keys.CHEESE_DELETE_SUCCESS].format(
                count,
                cheese_type,
                batch_number
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_text
            )
            await self.logger.logActivity(success_text, update, context)
            context.user_data.clear()
            return ConversationHandler.END
