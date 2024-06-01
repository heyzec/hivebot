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

from heyzec_bot.tenant_bot import TenantBot
from heyzec_bot.host_bot import HostBot
from heyzec_bot.mocks import MockApplicationBuilder
from heyzec_bot.root_handler import get_root_handler


TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

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
    for entry in os.scandir('bots'):
        path = entry.name
        if entry.is_file():
            if path == '__init__.py' or path[-3:] != '.py':
                continue
            module_name = f"bots.{path[:-3]}"
        elif entry.is_dir():
            if path == '__pycache__':
                continue
            load_dotenv(f"bots/{path}/.env")
            module_name = f"bots.{path}"
        else:
            continue

        sys.path.append(f"bots/{path}")
        bot_module = importlib.import_module(module_name)
        bot_module.main()
        handlers = mock_application_builder.get_handlers()

        bot = TenantBot(module_name, handlers)
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

