class OldApp:
    def __init__(self):
        self.handlers = []
        self.commands = []


    @property
    def job_queue(self):
        return self.app.job_queue

    @property
    def bot_data(self):
        return self.app.bot_data

    @bot_data.setter
    def bot_data(self, data: dict):
        # Beware of https://github.com/python-telegram-bot/python-telegram-bot/issues/3212
        # TODO: We need isolation
        # self.post_inits.append(data)
        raise NotImplementedError

    @classmethod
    def post_init(cls, callback):
        cls.post_inits.append(callback)


    @classmethod
    def prep(cls):
        # app = ApplicationBuilder().token(TELE_API_TOKEN).build()
        persistence = PicklePersistence(filepath="persistence.pickle")
        builder = ApplicationBuilder().token(TELE_API_TOKEN).persistence(persistence)

        async def post_init(application):
            for callback in cls.post_inits:
                callback(application)

        builder.post_init(post_init)

        app = builder.build()
        cls.app = app

    @classmethod
    def run(cls):
        app = cls.app

        conv_handler = get_conv_handler(cls)
        app.add_handler(conv_handler)

        inform_handler = MessageHandler(filters.TEXT, cls.inform)
        app.add_handler(inform_handler)

        cls.base_handlers = [inform_handler]
        app.run_polling()

