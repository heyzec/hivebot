import os

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)


STARTED = 1

async def get_user_info(update, context):
    await update.message.reply_text("info here")

async def start(update, context):
    await update.message.reply_text("User info mode activated")
    return STARTED

async def user_info(update, context):
    message = update.message

    from_user_id = message.from_user.id
    chat_id = message.chat.id
    forward_from_user_id = message.forward_from.id if message.forward_from is not None else None
    forward_from_chat_id = message.forward_from_chat.id if message.forward_from_chat is not None else None
    info = dict(
        from_user_id=from_user_id,
        chat_id=chat_id,
        forward_from_user_id=forward_from_user_id,
        forward_from_chat_id=forward_from_chat_id,
    )
    await message.reply_text(str(info))


async def cancel(update, context):
    return ConversationHandler.END


conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STARTED: [MessageHandler(filters.ALL, user_info)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
)

from dotenv import load_dotenv

load_dotenv()

TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')

def main():
    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    app.add_handler(conv_handler)

if __name__ == "__main__":
    main()
