import asyncio
from contextlib import contextmanager
import multiprocessing

from telegram.ext import Application

from heyzec_bot.app import prep


async def run(app: Application, stop_event):
    await app.initialize()
    assert app.updater is not None
    await app.updater.start_polling()
    await app.start()
    while True:
        if not stop_event.is_set():
            await asyncio.sleep(1)
        else:
            break
    await app.updater.stop()
    await app.stop()
    await app.shutdown()

def runner(app: Application, stop_event):
    asyncio.run(run(app, stop_event))


@contextmanager
def bot_fixture():
    """A fixture to setup and teardown the telegram bot."""
    # By wrapping it in a context manager, we can change scope
    # https://github.com/pytest-dev/pytest/issues/3425

    stop_event = multiprocessing.Event()
    app = prep()

    p = multiprocessing.Process(target=runner, args=(app, stop_event))
    p.start()
    yield
    stop_event.set()
    p.join()

