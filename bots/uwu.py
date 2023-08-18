import os

from telegram.ext import ApplicationBuilder
from telegram.ext import (
        CommandHandler,
        MessageHandler,
        filters,
)

from app import register

async def hello(update, _context):
    await update.message.reply_text("Good day, I can only say /hello!")

async def echo(update, _cdontext):
    await update.message.reply_text(update.message.text)


TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')

@register('UwuBot')
def main(app):
    app.add_handler(CommandHandler('hello', hello))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    app.run_polling()

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    main(app)
