import os
import importlib

from dotenv import load_dotenv
import importhook

from heyzec_bot.mocks import MockApplicationBuilder
from heyzec_bot.app import start
from heyzec_bot.tenant_bot import TenantBot

# # this logs to stdout and I think it is flushed immediately
# log_handler = logging.StreamHandler(stream=sys.stdout)
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().addHandler(log_handler)

load_dotenv()
TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')



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



if __name__ == "__main__":
    apps = []
    tenant_bots = load_bots()
    start(tenant_bots)
