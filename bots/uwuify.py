import os

import dotenv

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

def uwuify(s):
    lookup = {'ew': 'e', 'e': 'ew', 'E': 'ew', 'OwO': 'o', 'O': 'OwO', 'o': 'OwO', 'r': 'w', 'R': 'w', 'l': 'w', 'L': 'w'}
    for k, v in lookup.items():
        s = s.replace(k, v)
    return s

async def start(update, context):
    await update.message.reply_text("Send me some text and I will respond in uwu-speak!")

async def echo(update, context):
    await update.message.reply_text(uwuify(update.message.text))


def main():
    dotenv.load_dotenv()
    TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
    assert TELE_API_TOKEN is not None

    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    app.run_polling()

if __name__ == "__main__":
    main()
