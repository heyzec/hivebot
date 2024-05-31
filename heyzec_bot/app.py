from __future__ import annotations
import os

from telegram import BotCommand, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        PicklePersistence,
        filters,
)

from heyzec_bot.host_bot import HostBot


STARTED = 1
TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

async def switch(update, context):
    try:
        bot_name = update.message.text.split()[1]
    except IndexError:
        text = "No bot specified. Please specify a bot:"
        bot_names = list(bot.name for bot in host.bots)
        reply_keyboard = [[bot_name] for bot_name in bot_names]
        await update.message.reply_text(
            text, reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Pick a bot?"
            ),
        )
        return STARTED


    bot = host.switch_to_bot(bot_name)

    if bot is None:
        await update.message.reply_text("No such bot")
        return

    final = []
    for command, description in bot.commands:
        final.append(BotCommand(command, description))
    await context.application.bot.set_my_commands(final)

    await update.message.reply_text(f"Activated {bot_name} with {len(bot.handlers)} handlers.")
    return ConversationHandler.END

async def free(update, context):
    bot_name = update.message.text
    bot = host.switch_to_bot(bot_name)
    if bot is None:
        text = f"Bot {bot_name} does not exist!"
    else:
        text = f"Activated {bot_name} with {len(bot.handlers)} handlers."

    await update.message.reply_text(text,
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def inform(update, context):
    await update.message.reply_text(
        "None of the bots are active. Please select one using /switch")


def get_conv_handler():
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("switch", switch)],
            states={
                STARTED: [
                    CommandHandler("switch", switch),
                    MessageHandler(filters.TEXT, free),
                ],
            },
            fallbacks=[],
    )
    return conv_handler



def make_global(host_):
    global host
    host = host_

def start(tenant_bots):
    # dotenv.load_dotenv()
    TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
    assert TELE_API_TOKEN is not None

    persistence = PicklePersistence(filepath="persistence.pickle")
    builder = ApplicationBuilder().token(TELE_API_TOKEN).persistence(persistence)
    app = builder.build()

    host = HostBot()
    host.app = app
    host.bots = tenant_bots

    conv_handler = get_conv_handler()
    app.add_handler(conv_handler)

    base_handlers = []
    inform_handler = MessageHandler(filters.TEXT, inform)
    base_handlers.append(inform_handler)

    host.base_handlers = base_handlers
    for handler in base_handlers:
        app.add_handler(handler)

    make_global(host)
    app.run_polling()

