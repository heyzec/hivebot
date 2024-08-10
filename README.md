# HiveBot

HiveBot simplifies the process of hosting multiple [PTB](https://python-telegram-bot.org/) Telegram bots by leveraging request multiplexing to the appropriate bot handlers based on the selected bot in each chat session.

Hosting multiple Telegram bots typically requires each bot to have its own dedicated bot account and server configuration, which can be a chore.
With HiveBot, developers can consolidate multiple bots within a single account.
Simply add the tenant bot code to the dedicated folder within HiveBot's directory structure and HiveBot then handles the routing of incoming messages to the respective bot handlers based on the selected bot in each chat session.

## Quickstart

1. You will need to get your own Telegram API token from [@BotFather](https://t.me/botfather). Click [here](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) for the instructions.

1. Setup the necessary environment variables by copying `.env.template` to `.env` and editing `.env`.

1. Start HiveBot. Some example bots have already been added to the `bots` folder.
    ```
    python main.py
    ```
    You may need to use Poetry to install the necessary Python dependencies first. If you are using Nix, just `nix run` will suffice!

1. In Telegram, navigate to your bot chat.
    - Send a `/start` first if necessary (Telegram requires users to send a `/start` before bots can receive subsequent messages).
    - Send `/switch` to toggle between tenant bots.

## Adding tenant bots

Additional tenant bots can be added to HiveBot using the dedicated [`bots`](./bots) folder.
The code for each tenant bot can be a single file or multiple files consolidated within a folder.
There are minimal restrictions on the structure of the code of the tenant bots:
- **For bots with single Python file**: Ensure that the file has a `main()` function.
- **For bots with a folder**: Ensure that the folder contains a `main.py` with a `main()` function.

## How it works
HiveBot works by hijacking the `telegram` import that the PTB library provides, modifying the behaviour of [`telegram.ext.ApplicationBuilder`](https://docs.python-telegram-bot.org/en/stable/telegram.ext.applicationbuilder.html) used to build a PTB [`Application`](https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html) instance.
The benefit of this approach is that there is no need to design APIs that wrap what PTB already provides.
Hence, each tenant bot can run as part of HiveBot or run standalone without any code changes.


