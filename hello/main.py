from bot import Bot
from telegram.ext import (
        CommandHandler,
        MessageHandler,
        filters,
)

print("YAY")
async def start(update, context):
    await update.message.reply_text("hello!")

async def echo(update, context):
    # DISABLE THIS, ENSURE IT DOES NOT ECHO IN GROUPS!!!
    pass
    # await update.message.reply_text(update.message.text)

class HelloWorldBot(Bot):

    def initialise(self):
        self.add_handler(CommandHandler('start', start))
        self.add_handler(MessageHandler(filters.TEXT, echo))

Bot = HelloWorldBot
