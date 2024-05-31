import os
import importlib

from dotenv import load_dotenv
import importhook
from heyzec_bot import host_bot

from heyzec_bot.mocks import MockApplicationBuilder
from heyzec_bot.tenant_bot import TenantBot

# # this logs to stdout and I think it is flushed immediately
# log_handler = logging.StreamHandler(stream=sys.stdout)
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().addHandler(log_handler)

load_dotenv()
TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')





from heyzec_bot.app import start, load_bots

if __name__ == "__main__":
    start()
