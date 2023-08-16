from bot import Bot
from telegram.ext import (
        CommandHandler,
        MessageHandler,
        filters,
)

async def hello(update, context):
    await update.message.reply_text("Good day!")

class HelloWorldBot(Bot):

    def initialise(self):
        self.add_handler(CommandHandler('hello', hello))

Bot = HelloWorldBot
