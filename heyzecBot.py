# heyzecBot aims to handle credentials that are used in my @heyzecBot.# What the bot actually does can be hot swapped using other python files.
from telegram.ext import ApplicationBuilder
import asyncio
import os
from telegram.ext import Updater
import logging
import sys



# this logs to stdout and I think it is flushed immediately
handler = logging.StreamHandler(stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

TOKEN = '**********:*******-******-********************'
ME = 000000000
import importlib

async def test(x):
    while True:
        #logging.info("hi")
        await asyncio.sleep(1)

if __name__ == '__main__':
    # from loaded.attach import Bot

    app = ApplicationBuilder().token(TOKEN).build()

    bots = []
    for folder in sorted(os.listdir('loaded')):
        # if module == '__init__.py' or module[-3:] != '.py':
        #     continue
        print(folder)
        module = importlib.import_module(f"loaded.{folder}.main")
        bots.append(module.Bot())

    for i, bot in enumerate(bots):
        print(i)
        bot._set_objects(app, None, None)
        bot.initialise()






    app.job_queue.run_once(test, 1)
    app.run_polling()
