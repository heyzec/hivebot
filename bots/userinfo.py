import os

import dotenv
from telegram import MessageOrigin

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode


STARTED = 1

async def start(update, context):
    await update.message.reply_text("User info mode activated")
    return STARTED

async def user_info(update, context):
    message = update.message
    info = {}

    info['from_user.id'] = message.from_user.id
    info['chat.id'] = message.chat.id

    if (origin := message.forward_origin):
        if origin.type == MessageOrigin.USER:
            info['forward_origin.sender_user.id'] = message.forward_origin.sender_user.id
        elif origin.type == MessageOrigin.CHAT:
            info['forward_origin.chat.id'] = message.forward_origin.chat.id
        elif origin.type == MessageOrigin.CHANNEL:
            info['forward_origin.chat.id'] = message.forward_origin.chat.id

    max_key_length = max(len(k) for k in info.keys())
    text = '\n'.join(f"`{k}`: `{' ' * (max_key_length - len(k))}` `{v}`" for k, v in info.items())
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


def main():
    dotenv.load_dotenv()
    TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
    assert TELE_API_TOKEN is not None

    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT, user_info))
    app.run_polling()

if __name__ == "__main__":
    main()
