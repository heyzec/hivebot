import asyncio
import multiprocessing
import os

from dotenv import load_dotenv
import pytest
import pytest_asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

from heyzec_bot.app import prep


async def run(app, stop_event):
    await app.initialize()
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

def runner(app, stop_event):
    asyncio.run(run(app, stop_event))


@pytest.fixture(autouse=True, scope="session")
def bot():
    load_dotenv()
    stop_event = multiprocessing.Event()
    app = prep()

    p = multiprocessing.Process(target=runner, args=(app, stop_event))
    p.start()
    yield
    stop_event.set()
    p.join()


# All parts of Telethon must run in the same event loop!
# Since we are using fixtures, we must force each test to also run in the session event loop
# This requires pytest-asyncio <= 0.21.1, see https://github.com/pytest-dev/pytest-asyncio/issues/706
@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def telegram_client():
    load_dotenv()
    api_id = int(os.environ.get("TELEGRAM_APP_ID"))
    api_hash = os.environ.get("TELEGRAM_APP_HASH")
    session_str = os.environ.get("TELEGRAM_APP_SESSION")

    client = TelegramClient(
        StringSession(session_str), api_id, api_hash, sequential_updates=True
    )
    await client.connect()
    await client.get_me()
    await client.get_dialogs()
    yield client
    await client.disconnect()
    await client.disconnected


@pytest_asyncio.fixture(autouse=True, scope="session")
async def conv(telegram_client):
    async with telegram_client.conversation(
        'a_very_cool_bot', timeout=10
    ) as conv:
        yield conv

@pytest_asyncio.fixture(autouse=True, scope="session")
async def group(telegram_client):
    async with telegram_client.conversation(
        'heyzec and My First Bot!', timeout=10
    ) as conv:
        yield conv
