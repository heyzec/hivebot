from __future__ import annotations

from telegram import BotCommand, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
        BaseHandler,
        CallbackContext,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        filters,
)



SWITCHING = 1

class AnyHandler(BaseHandler[Update, CallbackContext]):
    def check_update(self, update):
        # This handler will handle all updates
        return True

    async def handle_update(self, update, application, check_result, context):
        await super().handle_update(update, application, check_result, context)
        return ConversationHandler.END


def get_root_handler(host):

    async def switch(update, context):
        chat_id = update.message.chat.id
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
            return SWITCHING


        bot = host.switch_to_bot(chat_id, bot_name)

        if bot is None:
            await update.message.reply_text("No such bot")
            return

        # final = []
        # for command, description in bot.commands:
        #     final.append(BotCommand(command, description))
        # await context.application.bot.set_my_commands(final)

        await update.message.reply_text(f"Activated {bot_name} with {len(bot.handlers)} handlers.")
        return ConversationHandler.END

    async def select_bot(update, context):
        chat_id = update.message.chat.id
        bot_name = update.message.text
        bot = host.switch_to_bot(chat_id, bot_name)
        if bot is None:
            text = f"Bot {bot_name} does not exist!"
        else:
            text = f"Activated {bot_name} with {len(bot.handlers)} handlers."

        await update.message.reply_text(text,
            reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


    handler = ConversationHandler(
        entry_points=[
            CommandHandler("switch", switch),
            MessageHandler(filters.ALL, host.handle_update),
        ],
        states={
            SWITCHING: [
                CommandHandler("switch", switch),
                MessageHandler(filters.TEXT, select_bot),
            ],
        },
        fallbacks=[],
    )
    return handler


