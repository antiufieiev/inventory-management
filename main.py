import logging
import os

from telegram.ext import ApplicationBuilder

import database.storage
from command.addcheese import *
from command.adduser import *
from command.printdatabasestate import *
from command.printuserhistory import *
from command.putcheese import *
from command.removecheese import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command")


if __name__ == '__main__':

    database.storage.initStorage()
    token = ''
    if os.environ['PRODUCTION'] == 'true':
        token = os.environ['PRODUCTION_TELEGRAM_TOKEN']
    else:
        token = os.environ['DEBUG_TELEGRAM_TOKEN']

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(AddUserCommand().createTelegramConversation())
    application.add_handler(AddCheeseCommand().createTelegramConversation())
    application.add_handler(PutCheeseCommand().createTelegramConversation())
    application.add_handler(RemoveCheeseCommand().createTelegramConversation())
    application.add_handler(UserHistoryCommand().createTelegramConversation())
    application.add_handler(DatabaseStateCommand().createTelegramCommand())
    application.add_handler(MessageHandler(filters.TEXT, unknown))

    application.run_polling()
