from typing import Optional
from telegram import Update

from telegram.ext import Application, CallbackContext

from .tenant_bot import TenantBot

class HostBot:
    def __init__(self, app: Application):
        self.app = app
        self.bots: list[TenantBot]
        self.active_bots: dict[int, list[str]] = {}

        async def post_init(app):
            self.active_bots = app.bot_data.get('active_bots', {})
            app.bot_data['active_bots'] = self.active_bots

        app.post_init = post_init

    def get_active_bots(self, chat_id: int):
        if chat_id not in self.active_bots:
            return []

        bot_names = self.active_bots[chat_id]
        bots = []
        for bot_name in bot_names:
            for bot in self.bots:
                if bot.name == bot_name:
                    bots.append(bot)
                    break
        return bots

    def set_active_bot(self, chat_id: int, bot_name: str) -> Optional[TenantBot]:
        if bot_name not in (bot.name for bot in self.bots):
            return None

        self.active_bots[chat_id] = [bot_name]

        for bot in self.bots:
            if bot.name == bot_name:
                return bot
        assert False


    async def handle_update(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        active_bots_for_chat = self.get_active_bots(chat_id)

        if len(active_bots_for_chat) == 0:
            await update.effective_chat.send_message(
                "None of the bots are active. Please select one using /switch")
            return

        for bot in active_bots_for_chat:
            handled = False
            for handler in bot.handlers:
                check_result = handler.check_update(update)
                to_handle = not(check_result is None or check_result is False)
                if to_handle:
                    await handler.handle_update(update, self.app, check_result, context)
                    handled = True
                    break
            if handled:
                break






