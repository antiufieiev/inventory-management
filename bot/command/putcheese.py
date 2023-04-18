from datetime import datetime

import peewee
import pytz
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, filters, CallbackQueryHandler

from bot.command.basecommand import *
from bot.command.default_fallback import *
from bot.database.model import CheeseVariants, Batches, database_proxy
from bot.feature.activitylogger import ActivityLogger
from bot.feature.permissionchecker import checkUserAccess
from bot.localization.localization import *


class PutCheeseCommand(BaseConversation):
    STATE_INIT, STATE_TYPE_SELECTED, STATE_COUNT_SELECTED, STATE_PACKED_SELECTED, STATE_COMMENT = range(5)
    ADMIN, EMPLOYEE = range(2)

    def __init__(self):
        super(PutCheeseCommand, self).__init__(
            command_name="putcheese",
            fallback_command=DefaultFallbackCommand()
        )

    def createStatesWithHandlers(self):
        return {
            self.STATE_TYPE_SELECTED: [
                CallbackQueryHandler(
                    self.handleInlineButtonClick,
                    pattern=f"^{self.callback_filter}")
            ],
            self.STATE_PACKED_SELECTED: [
                CallbackQueryHandler(
                    self.handleInlineButtonClick,
                    pattern=f"^{self.callback_filter}"
                )
            ],
            self.STATE_COUNT_SELECTED: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCountEntered)],
            self.STATE_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleCommentEntered)]
        }

    async def handleInlineButtonClick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        print(query.data)
        filtered = self.omitFilter(query.data).partition(':')
        state = filtered[0]
        data = filtered[2]
        new_state = self.STATE_TYPE_SELECTED
        if state == str(self.STATE_INIT):
            new_state = await self.handleTypeSelected(data, update, context)
        if state == str(self.STATE_PACKED_SELECTED):
            new_state = await self.handlePackedEntered(data, update, context)

        await query.answer()
        return new_state

    async def executeCommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if checkUserAccess(update) >= AccessLevel.EMPLOYEE:
            variants = CheeseVariants.select()
            data = list(
                map(lambda variant: InlineKeyboardButton(
                    text=variant.name,
                    callback_data=f"{self.callback_filter}{self.STATE_INIT}:{variant.name}"
                ), variants)
            )
            chunks = [data[x:x + 3] for x in range(0, len(data), 3)]
            reply_markup = InlineKeyboardMarkup(chunks)

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

    async def handleTypeSelected(self, cheese_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not cheese_type.strip():
            await context.bot.send_message(chat_id=update.effective_chat.id, text=localization_map[Keys.ERROR_EMPTY])
            return self.STATE_TYPE_SELECTED

        type_variant = CheeseVariants.select().where(CheeseVariants.name == cheese_type)
        if type_variant.count() != 1:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_NO_TYPE_EXIST]
            )
            return self.STATE_TYPE_SELECTED

        context.user_data["cheese_id"] = type_variant[0].id

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ENTER_CHEESE_AMOUNT]
        )
        return self.STATE_COUNT_SELECTED

    async def handleCountEntered(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        count = update.message.text
        context.user_data["count"] = count
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

    async def handlePackedEntered(self, packed_state: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

        context.user_data["is_packed"] = is_packed
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization_map[Keys.ENTER_COMMENT]
        )
        return self.STATE_COMMENT

    async def handleCommentEntered(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.text.strip():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_EMPTY]
            )
            return self.STATE_COMMENT

        comment = update.message.text
        count = context.user_data["count"]
        cheese_id = context.user_data["cheese_id"]
        is_packed = context.user_data["is_packed"]
        try:
            with database_proxy.connection_context():
                batch = self.generateBatchName(cheese_id)
                Batches(
                    cheese_id=cheese_id,
                    batch_number=batch,
                    count=count,
                    packed=is_packed,
                    comment=comment
                ).save(force_insert=True)
                input_text = localization_map[Keys.ADD_CHEESE_SUCCESS].format(batch, count)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=input_text
                )
                active = ActivityLogger(self.command_name, update.effective_user.id, input_text)
                await active.logActivity(update, context)
                return ConversationHandler.END
        except peewee.IntegrityError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization_map[Keys.ERROR_BATCH_INSERT]
            )
            return self.STATE_COMMENT

    @staticmethod
    def generateBatchName(cheese_id: int) -> str:
        european = pytz.timezone('Europe/Kyiv')
        date = datetime.now(european)
        batch = date.strftime("%d%m%y") + str(cheese_id)
        existing_batches = Batches.select().order_by(Batches.batch_number).where(
            Batches.cheese_id == cheese_id and Batches.batch_number.startswith(batch)
        )
        suffix = ""
        if existing_batches.count() > 0:
            suffix = f"-{existing_batches.count()}"

        return batch + suffix
