import os
import random


from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ConversationHandler,
        MessageHandler,
        filters,
)

from dotenv import load_dotenv

from app import register

load_dotenv()

TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

preferences = {
        'mixed rice': 50,
        'chicken rice': 10,
        'ban mian': 10,
        'fishball noodles': 10,
        'laksa': 5,
}


async def start(update, context):
    print("Hi")
    await update.message.reply_text(
            "Hello for starting me, just type anything and I'll roll the dice!")
    await update.message.reply_text("""
anything: get a preference
/start: show this menu again
/show: show this menu again
""")
    return STARTED

async def show(update, context):
    await update.message.reply_text("Your preferences are:")
    await update.message.reply_text(str(preferences))

async def cancel(update, context):
    await update.message.reply_text("Okay cancelled")

async def food(update, context):
    item = random.choices(list(preferences.keys()),
                       weights=list(preferences.values()))[0]
    await update.message.reply_text(f"Let's have {item} today!")

STARTED = 1

conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STARTED: [
                CommandHandler('show', show),
                MessageHandler(filters.TEXT, food),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
)


@register('FoodBot')
def main(app):
    app.add_handler(conv_handler)
    # app.add_handler(CommandHandler('switch', food))
    app.run_polling()

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    main(app)
