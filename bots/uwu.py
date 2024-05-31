import os

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

async def hello(update, _context):
    await update.message.reply_text("Good day, I can only say /hello!")

async def echo(update, _cdontext):
    await update.message.reply_text(update.message.text)


TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')

def main():
    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    app.add_handler(CommandHandler('hello', hello))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    app.run_polling()

if __name__ == '__main__':
    main()
