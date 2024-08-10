from __future__ import annotations
import os
import sys

from dotenv import load_dotenv
import importhook
import importlib

from telegram.ext import (
        ApplicationBuilder,
        PicklePersistence,
)

from hivebot.tenant_bot import TenantBot
from hivebot.host_bot import HostBot
from hivebot.mocks import MockApplicationBuilder
from hivebot.root_handler import get_root_handler


TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Folder to look for tenant bots
BOTS_FOLDER = "bots"

def load_bots():
    """Load all tenant bots in the specified folder."""
    mock_application_builder = MockApplicationBuilder()

    # Hijack the telegram.ext module
    @importhook.on_import('telegram.ext')
    def on_import(module):
        new_module = importhook.copy_module(module)
        setattr(new_module, 'ApplicationBuilder', mock_application_builder)
        return new_module

    bots = []
    for entry in os.scandir(BOTS_FOLDER):
        path = entry.name
        if entry.is_file():
            if path == '__init__.py' or not path.endswith('.py'):
                continue

            # Treat the single file as a part of the BOTS_FOLDER module
            basename = os.path.splitext(path)[0]
            module_name = f"{BOTS_FOLDER}.{basename}"
            bot_name = basename
        elif entry.is_dir():
            if path == '__pycache__':
                continue

            if not os.path.exists(os.path.join(BOTS_FOLDER, path, 'main.py')):
                print(f"{BOTS_FOLDER}/{path} does not contain main.py, skipping...")
                continue

            # Pretend to run the main.py from within the folder
            module_name = "main"
            sys.path.insert(0, os.path.join(BOTS_FOLDER, path))
            load_dotenv(os.path.join(BOTS_FOLDER, path, '.env'))
            bot_name = f"{path}"
        else:
            continue


        try:
            bot_module = importlib.import_module(module_name)
        except Exception as e:
            print(f"An error occurred while importing {bot_name}, skipping: {e}")
            continue

        try:
            entrypoint = bot_module.main
        except AttributeError:
            relpath = os.path.relpath(bot_module.__file__, os.getcwd())
            print(f"{relpath} has no main function, skipping")
            continue

        try:
            entrypoint()
        except Exception as e:
            print(f"An error occurred while starting up {bot_name}, skipping: {e}")
            continue
        handlers = mock_application_builder.get_handlers()

        bot = TenantBot(bot_name, handlers)
        bots.append(bot)


    messages = []
    for bot in bots:
        messages.append(f"{bot.name} ({len(bot.handlers)})")
    print(f"Loaded {len(bots)} bots: {', '.join(messages)}")
    return bots

def prep():
    TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
    assert TELE_API_TOKEN is not None

    host = HostBot()

    persistence = PicklePersistence(filepath="persistence.pickle")
    builder = ApplicationBuilder().token(TELE_API_TOKEN).persistence(persistence)
    app = builder.build()
    host.app = app
    host.bots = load_bots()

    conv_handler = get_root_handler(host)
    app.add_handler(conv_handler)
    return app

def start():
    app = prep()
    app.run_polling()

async def start_nonblocking(tenant_bots):
    app = prep()
    await app.initialize()
    await app.updater.start_polling()
    await app.start()

