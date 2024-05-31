from typing import Optional
from telegram import Update

from telegram.ext import Application, CallbackContext
from .tenant_bot import TenantBot

class HostBot:
    app: Application
    bots: list[TenantBot]
    active_bot: Optional[TenantBot] = None
    base_handlers: list[object]

    active_bots: dict[int, set[TenantBot]]

    def __init__(self) -> None:
        self.active_bots = {}


    def get_active_bots(self, chat_id):
        if chat_id not in self.active_bots:
            return []
        return self.active_bots[chat_id]

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






    def switch_to_bot(self, chat_id, bot_name):
        if bot_name not in (bot.name for bot in self.bots):
            return None

        # Activate new bot
        bot = list(filter(lambda bot: bot.name == bot_name, self.bots))[0]

        self.active_bots[chat_id] = [bot]
        return bot

