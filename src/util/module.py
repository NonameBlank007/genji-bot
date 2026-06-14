from telegram.ext import Application


class Module:
    @classmethod
    def setup(cls, app: Application):
        raise NotImplementedError
