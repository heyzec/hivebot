"""
Simple monitoring service where the program that is expected to stay alive needs to ping this bot.
If no ping is received within an extended period of time, a notification is send to the user.
"""
import asyncio
from datetime import datetime
from enum import Enum
import os
import socket
import time
from typing import Optional


from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
)

from dotenv import load_dotenv


from app import register


class Mode(Enum):
    ON = 'on'
    OFF = 'off'
    MIXED = 'mixed'



last = None

def format_time(timestamp: Optional[float]):
    if timestamp is None:
        return "never"
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%s %d %b %Y')

async def setmode(update, context):
    valid_modes = [mode.value for mode in Mode]
    error_text = f"Invalid input, the acceptable modes are: {valid_modes}"

    words = update.message.text.split()
    if len(words) < 2:
        await update.message.reply_text(error_text)
        return
    mode = words[1]
    if Mode[mode.upper()] not in Mode:
        valid_modes = [mode.value for mode in Mode]
        await update.message.reply_text(error_text)
        return

    mode = Mode[mode.upper()]

    context.bot_data['mode'] = mode

    if mode == Mode.ON:
        text = "Okay, the bot will alert on every action."
    elif mode == Mode.OFF:
        text = "Okay, the bot not alert at all."
    elif mode == Mode.MIXED:
        text = "Okay, the bot will alert only if the watchee is dead."
    else:
        assert False


    await update.message.reply_text(text)



async def send_dead(context):
    while last is not None and time.time() - last < INTERVAL:
        await asyncio.sleep(INTERVAL - (time.time() - last) + 5)
    if context.bot_data['mode'] in (Mode.ON, Mode.MIXED):
        await context.bot.send_message(ADMIN_CHAT_ID,
                f"Dead, last seen at {format_time(last)}.")


async def serve_client(conn, addr, context):
    loop = asyncio.get_running_loop()
    try:
        ch = None
        buffer = b''
        while len(buffer) != len(PASSPHRASE):
            ch = await loop.sock_recv(conn, 1)
            if len(ch) == 0:
                return
            buffer += ch
        if buffer != PASSPHRASE.encode():
            return
        data = b''
        while ch != b'\n':
            ch = await loop.sock_recv(conn, 1)
            if len(ch) == 0:
                return
            data += ch
        print(data)
    except OSError:
        print("closed connection or timeout")
        return

    conn.sendall(b"Okay")

    global last
    last = time.time()
    if context.bot_data['mode'] == Mode.ON:
        await context.bot.send_message(ADMIN_CHAT_ID,
                f"He's alive from {data.decode()}, as of {format_time(last)}!!")

def initialise_service():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Without this, sometimes port in use due to socket TIME_WAIT
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Without this, loop.sock_accept will also still block
    sock.setblocking(False)

    sock.bind((HOST, PORT))
    sock.listen()

    # Using a callback pattern over while loop so that shutdowns are graceful
    # TODO: Still not ideal. We need to kill the last await
    async def listen_once(context):
        # if 'n_jobs' not in context.bot_data:
        #     context.bot_data['n_jobs'] = 0
        # if 'mode' not in context.bot_data:
        #     context.bot_data['mode'] = Mode.HALF

        if context.bot_data['n_jobs'] != 0:
            return

        context.bot_data['n_jobs'] += 1
        loop = asyncio.get_running_loop()
        try:
            async with asyncio.timeout(5):
                conn, addr = await loop.sock_accept(sock)
        except TimeoutError:
            return
        conn.settimeout(1)
        print(f"Received connection from {addr}!")
        await serve_client(conn, addr, context)
        conn.close()
        context.bot_data['n_jobs'] -= 1

    return listen_once

def cleanup_service():
    # TODO
    pass




HOST = os.environ.get('HOST')
print(HOST)
PORT = int(os.environ.get('PORT'))
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID'))
INTERVAL = int(os.environ.get('INTERVAL'))
PASSPHRASE = os.environ.get('PASSPHRASE')


@register('AliveBot')
def main(app):

    app.bot_data = {
        'n_jobs': 0,
        'mode': Mode.OFF
    }
    app.add_handler(CommandHandler('setmode', setmode))

    service_callback = initialise_service()

    app.job_queue.run_repeating(service_callback, 1, job_kwargs={'max_instances': 2})
    app.job_queue.run_repeating(send_dead, INTERVAL)
    app.run_polling()

if __name__ == '__main__':
    load_dotenv()
    TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN')
    assert TELE_API_TOKEN is not None

    app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    main(app)
