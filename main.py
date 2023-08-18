import os
import sys
import logging
import importlib

from app import App
from dotenv import load_dotenv

# # this logs to stdout and I think it is flushed immediately
# log_handler = logging.StreamHandler(stream=sys.stdout)
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().addHandler(log_handler)

load_dotenv()
TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')

# Load all modules (plugins) here
def load():
    apps = []
    for entry in os.scandir('bots'):

        path = entry.name
        if entry.is_file():
            if path == '__init__.py' or path[-3:] != '.py':
                continue
            module_name = f"bots.{path[:-3]}"
        elif entry.is_dir():
            if path == '__pycache__':
                continue
            x = load_dotenv(f"bots/{path}/.env")
            module_name = f"bots.{path}"
        else:
            continue
        importlib.import_module(module_name)
        apps.append(module_name)
    print(f"Loaded {len(apps)} bots: {', '.join(apps)}")


if __name__ == '__main__':
    App.prep()
    load()
    App.run()
