from typing import Optional

from telegram.ext import Application
from .tenant_bot import TenantBot


class HostBot:
    app: Application
    bots: list[TenantBot]
    active_bot: Optional[TenantBot] = None
    base_handlers: list[object]


    def switch_to_bot(self, bot_name):
        app = self.app
        if bot_name not in (bot.name for bot in self.bots):
            return None

        # Deactivate old bot
        if self.active_bot is not None:
            for handler in self.active_bot.handlers:
                app.remove_handler(handler)
        else:
            for handler in self.base_handlers:
                app.remove_handler(handler)

        # Activate new bot
        bot = list(filter(lambda bot: bot.name == bot_name, self.bots))[0]
        print(bot_name, bot)
        for handler in bot.handlers:
            app.add_handler(handler)
        self.active_bot = bot
        return bot

