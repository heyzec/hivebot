from __future__ import annotations

import abc
from typing import Callable, Optional
import os

from dotenv import load_dotenv

from telegram import BotCommand, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
        ApplicationBuilder,
        Application,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        filters,
)

# This should not be necessary, but idk why now both appstarter.py and app.py needs
load_dotenv()

STARTED = 1

async def switch(cls, update, context):
    try:
        bot_name = update.message.text.split()[1]
    except IndexError:
        text = "No bot specified. Please specify a bot:"
        bot_names = list(cls.all_apps.keys())
        reply_keyboard = [[bot_name] for bot_name in bot_names]
        await update.message.reply_text(
            text, reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Pick a bot?"
            ),
        )
        return STARTED


    bot = cls.switch_to_bot(bot_name)

    if bot is None:
        await update.message.reply_text("No such bot")
        return

    final = []
    for command, description in bot.commands:
        final.append(BotCommand(command, description))
    await context.application.bot.set_my_commands(final)

    await update.message.reply_text(f"Activated {bot_name} with {len(bot.handlers)} handlers.")
    return ConversationHandler.END

async def free(cls, update, context):
    bot_name = update.message.text
    bot = cls.switch_to_bot(bot_name)
    if bot is None:
        text = f"Bot {bot_name} does not exist!"
    else:
        text = f"Activated {bot_name} with {len(bot.handlers)} handlers."

    await update.message.reply_text(text,
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END



def get_conv_handler(cls):
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("switch", cls.switch)],
            states={
                STARTED: [
                    CommandHandler("switch", cls.switch),
                    MessageHandler(filters.TEXT, cls.free),
                ],
            },
            fallbacks=[],
    )
    return conv_handler




TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

class App(abc.ABC):
    app: Application
    all_apps = {}
    active_app: Optional[App] = None

    def __init__(self):
        self.handlers = []
        self.commands = []

    def run_polling(self):
        """Do nothing"""

    def add_handler(self, handler, group=0):
        if isinstance(handler, CommandHandler):
            command = list(handler.commands)[0]
            if command == 'switch':
                message = f"/{command} is a reserved command!"
                raise Exception(message)


            description = handler.callback.__name__
            self.commands.append((command, description))

        self.handlers.append(handler)
        # self.app.add_handler(handler, group=group)

    def remove_handler(self, handler, group=0):
        self.handlers.remove(handler)
        # self.app.remove_handler(handler, group=group)

    @property
    def job_queue(self):
        return self.app.job_queue

    @property
    def bot_data(self):
        return self.app.bot_data

    @bot_data.setter
    def bot_data(self, data):
        # TODO: We need isolation
        self.app.bot_data = data


    @classmethod
    def register(cls, app_name: str):
        def wrapped(func: Callable):
            new_app = cls()
            func(new_app)
            if app_name in cls.all_apps:
                raise Exception(f"{app_name} is already taken!")
            cls.all_apps[app_name] = new_app
            return func
        return wrapped

    @classmethod
    def switch_to_bot(cls, bot_name):
        app = cls.app

        if bot_name not in cls.all_apps:
            return None

        # Deactivate old bot
        if cls.active_app is not None:
            for handler in cls.active_app.handlers:
                app.remove_handler(handler)
        else:
            for handler in cls.base_handlers:
                app.remove_handler(handler)

        # Activate new bot
        bot = cls.all_apps[bot_name]
        for handler in bot.handlers:
            app.add_handler(handler)
        cls.active_app = bot
        return bot



    @classmethod
    async def switch(cls, update, context):
        return await switch(cls, update, context)

    @classmethod
    async def free(cls, update, context):
        return await free(cls, update, context)


    @classmethod
    async def inform(cls, update, context):
        await update.message.reply_text(
            "None of the bots are active. Please select one using /switch")
    @classmethod
    def prep(cls):
        app = ApplicationBuilder().token(TELE_API_TOKEN).build()
        cls.app = app

    @classmethod
    def run(cls):
        # app.add_handler(CommandHandler('switch', cls.switch))
        app = cls.app

        conv_handler = get_conv_handler(cls)
        app.add_handler(conv_handler)

        inform_handler = MessageHandler(filters.TEXT, cls.inform)
        app.add_handler(inform_handler)

        cls.base_handlers = [inform_handler]
        app.run_polling()

register = App.register
