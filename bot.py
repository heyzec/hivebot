import abc
print("BOT IS GOOD")
from telegram.ext import Application
from telegram import Bot as TelegramBot


class Bot(abc.ABC):
    _JOB_KWARGS = {
            'misfire_grace_time': None
    }

    def __init__(self):
        self.app: Application
        self.bot: TelegramBot
        self.dispatcher = None

    def _set_objects(self, app, bot, dispatcher):
        self.app = app
        self.bot = bot
        self.dispatcher = dispatcher


    def add_handler(self, handler, group=0):
        self.app.add_handler(handler, group=group)

    def remove_handler(self, handler, group=0):
        self.app.remove_handler(handler, group=group)

    @abc.abstractmethod
    def initialise(self):
        pass

    def run_repeating(self, callback, interval):
        assert self.app.job_queue is not None
        self.app.job_queue.run_repeating(callback, interval, job_kwargs=Bot._JOB_KWARGS)

    def run_once(self, callback, when):
        assert self.app.job_queue is not None
        self.app.job_queue.run_once(callback, when, job_kwargs=Bot._JOB_KWARGS)
