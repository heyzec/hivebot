from telegram.ext._handlers.commandhandler import CommandHandler

class MockApplication:
    def __init__(self) -> None:
        self.handlers = []

    def run_polling(self):
        # Do nothing
        pass

    def add_handler(self, handler, group=0):
        if isinstance(handler, CommandHandler):
            command = list(handler.commands)[0]
            if command == 'switch':
                message = f"/{command} is a reserved command!"
                raise Exception(message)


            description = handler.callback.__name__
            self.commands.append((command, description))

        self.handlers.append(handler)
        # self.app.add_handler(handler, group=group)

    def remove_handler(self, handler, group=0):
        self.handlers.remove(handler)
        # self.app.remove_handler(handler, group=group)

    def __getattr__(self, attrname):
        return self

    def __call__(self, *args, **kwargs):
        return self


class MockApplicationBuilder:
    def __init__(self) -> None:
        self.prev_attr = None
        self.mock_application = MockApplication()

    def __call__(self, *args, **kwargs):
        if self.prev_attr == 'build':
            self.prev_attr = None
            return self.mock_application
        return self

    def __getattr__(self, attrname):
        self.prev_attr = attrname
        return self

    def get_handlers(self):
        handlers = self.mock_application.handlers
        self.mock_application.handlers = []
        return handlers
