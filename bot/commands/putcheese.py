from datetime import datetime

import peewee
import pytz
from telegram.ext import MessageHandler, filters, CallbackQueryHandler

from bot.commands.default_fallback import *
from bot.database.model import Batches, database_proxy, Packaging
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *
from bot.usecase import selectcountstate, selectpackagingusecase, selectispackagedusecase, selectcommentusecase, \
    selectcheesetypeusecase
from bot.usecase.state_values import *


class PutCheeseCommand(BaseConversation):

    def __init__(self):
        super(PutCheeseCommand, self).__init__(
            command_name="putcheese",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            STATE_WAIT_FOR_CHEESE_TYPE_SELECTION: [
                CallbackQueryHandler(
                    self.handleInlineButtonClick,
                    pattern=f"^{self.callback_filter}")
            ],
            STATE_WAIT_FOR_IS_PACKED_SELECTION: [
                CallbackQueryHandler(
                    self.handleInlineButtonClick,
                    pattern=f"^{self.callback_filter}"
                )
            ],
            STATE_WAIT_FOR_PACKAGING_SELECTION: [
                CallbackQueryHandler(
                    self.handleInlineButtonClick,
                    pattern=f"^{self.callback_filter}"
                )
            ],
            STATE_WAIT_FOR_COUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCountEntered)],
            STATE_WAIT_FOR_COMMENT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCommentResponse)]
        }

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        with database_proxy.connection_context():
            if checkUserAccess(update) >= AccessLevel.EMPLOYEE:
                return await selectcheesetypeusecase.prepareSelectCheeseTypeUseCase(self.callback_filter, update)
            else:
                await update.effective_message.reply_text(
                    text=localization_map[Keys.ACCESS_DENIED],
                )
                return ConversationHandler.END

    async def handleInlineButtonClick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        filtered = self.omitFilter(query.data).partition(':')
        state = filtered[0]
        data = filtered[2]
        new_state = STATE_WAIT_FOR_CHEESE_TYPE_SELECTION
        if state == str(STATE_CHEESE_TYPE_SELECTED):
            new_state = await self.handleTypeSelected(data, update, context)
        if state == str(STATE_WAIT_FOR_IS_PACKED_SELECTION):
            new_state = await self.handlePackedEntered(data, update, context)
        if state == str(STATE_WAIT_FOR_PACKAGING_SELECTION):
            new_state = await self.handlePackagingFormatSelected(data, update, context)

        await query.answer()
        return new_state

    async def handleTypeSelected(self, cheese_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcheesetypeusecase.onCheeseTypeSelected(cheese_type, update, context)
        if result != STATUS_SUCCESS:
            return result

        if checkUserAccess(update) >= AccessLevel.MANAGER:
            return await selectispackagedusecase.prepareIsPackagedState(self.callback_filter, update)
        else:
            return await selectcountstate.prepareCountState(update, context)

    async def handleCountEntered(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcountstate.handleCountEntered(update, context)
        if result != STATUS_SUCCESS:
            return result
        if checkUserAccess(update) >= AccessLevel.MANAGER:
            return await selectcommentusecase.prepareselectcommentusecase(update, context)
        else:
            context.user_data["comment"] = ""
            return await self.finalize(update, context)

    async def handlePackedEntered(self, packed_state: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectispackagedusecase.onIsPackagedStateSelected(packed_state, update, context)
        if result != STATUS_SUCCESS:
            return result
        if context.user_data["is_packed"]:
            return await selectpackagingusecase.preparePackagingState(self.callback_filter, update, context)
        else:
            return await selectcountstate.prepareCountState(update, context)

    @staticmethod
    async def handlePackagingFormatSelected(packaging_id: str, update: Update,
                                            context: ContextTypes.DEFAULT_TYPE) -> int:
        selectpackagingusecase.handlePackagingFormatSelected(packaging_id, context)
        return await selectcountstate.prepareCountState(update, context)

    async def handleCommentResponse(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result = await selectcommentusecase.handleCommentSelected(update, context)
        if result != STATUS_SUCCESS:
            return result
        return await self.finalize(update, context)

    async def finalize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        count = context.user_data["count"]
        cheese_id = context.user_data["cheese_id"]
        is_packed = context.user_data.get("is_packed")
        comment = context.user_data.get("comment")
        packaging_id = context.user_data.get("packaging_id")
        if packaging_id is not None:
            packaging_id = int(packaging_id)
        try:
            with database_proxy.connection_context():
                batch = self.generateBatchName(cheese_id)
                Batches(
                    cheese=cheese_id,
                    batch_number=batch,
                    count=count,
                    packaging_id=packaging_id,
                    comment=comment
                ).save(force_insert=True)
                if is_packed:
                    packagingModel = Packaging.get(Packaging.id == packaging_id)
                    input_text = localization_map[Keys.ADD_CHEESE_SUCCESS] \
                        .format(batch, count, packagingModel.packaging)
                elif checkUserAccess(update) > AccessLevel.EMPLOYEE:
                    input_text = localization_map[Keys.ADD_CHEESE_SUCCESS_NO_PACKAGING].format(batch, count)
                elif checkUserAccess(update) == AccessLevel.EMPLOYEE:
                    input_text = localization_map[Keys.EMPLOYEE_ADD_CHEESE_SUCCESS].format(batch, count)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=input_text
                )
                await self.logger.logActivity(input_text, update, context)
                context.user_data.clear()
                return ConversationHandler.END
        except peewee.IntegrityError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_BATCH_INSERT]
            )
            return ConversationHandler.END

    @staticmethod
    def generateBatchName(cheese_id: int) -> str:
        european = pytz.timezone('Europe/Kyiv')
        date = datetime.now(european)
        batch = date.strftime("%d%m%y") + str(cheese_id)
        existing_batches = Batches.select().order_by(Batches.batch_number).where(
            Batches.cheese == cheese_id and Batches.batch_number.startswith(batch)
        )
        suffix = ""
        if existing_batches.count() > 0:
            suffix = f"-{existing_batches.count()}"

        return batch + suffix
