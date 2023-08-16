import asyncio
from datetime import datetime
import os
import socket
import time
from typing import Optional

from bot import Bot

from telegram import (
        ReplyKeyboardRemove,
)

from telegram.ext import (
        CommandHandler,
        MessageHandler,
)

HOST = '0.0.0.0'
PORT = 17171
HEYZEC = 000000000
INTERVAL = 60

last = None

def format_time(time: Optional[float]):
    if time is None:
        return "never"
    return datetime.fromtimestamp(time).strftime('%H:%M:%s %d %b %Y')

# async def start(update, context):
#     await update.message.reply_text("hi",
#             reply_markup=ReplyKeyboardRemove())

async def on(update, context):
    context.bot_data['on'] = True
    await update.message.reply_text("Will alert on every notification")

async def off(update, context):
    context.bot_data['on'] = False
    await update.message.reply_text("Will only alert if Pi is dead")


async def alive(update, context):
    words = update.message.text.split()
    if len(words) < 2:
        await update.message.reply_text("Invalid input.")
        return
    mode = words[1]
    if mode not in ('on', 'off', 'half'):
        await update.message.reply_text("Invalid input.")

    context.bot_data['mode'] = mode
    await update.message.reply_text("Okay, mode changed.")



async def send_dead(context):
    while True:
        while last is not None and time.time() - last < INTERVAL:
            await asyncio.sleep(INTERVAL - (time.time() - last) + 5)
        if context.bot_data['mode'] in ('on', 'half'):
            await context.bot.send_message(HEYZEC,
                    f"Dead, last seen at {format_time(last)}.")
        await asyncio.sleep(INTERVAL)


async def serve_client(conn, addr, context):
    loop = asyncio.get_running_loop()
    try:
        passphrase = b''
        while len(passphrase) != 18:
            ch = await loop.sock_recv(conn, 1)
            if len(ch) == 0:
                return
            passphrase += ch
        if passphrase != b'laundrylostmysocks':
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
    if context.bot_data['mode'] in ('on'):
        await context.bot.send_message(HEYZEC,
                f"He's alive from {data.decode()}, as of {format_time(last)}!!")


async def service(context):
    # HACK
    if 'mode' not in context.bot_data:
        context.bot_data['mode'] = 'half'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        loop = asyncio.get_running_loop()
        # Without this, sometimes port in use due to socket TIME_WAIT
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Without this, loop.sock_accept will also still block
        sock.setblocking(False)

        sock.bind((HOST, PORT))
        sock.listen()
        while True:
            conn, addr = await loop.sock_accept(sock)
            conn.settimeout(1)
            print(f"Received connection from {addr}!")
            await serve_client(conn, addr, context)
            conn.close()



class AliveBot(Bot):
    def initialise(self):
        self.add_handler(CommandHandler('alive', alive))

        self.run_once(service, 1)
        self.run_once(send_dead, 1)

Bot = AliveBot









