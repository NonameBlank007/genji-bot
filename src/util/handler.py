from ..module import start


class Handlers:
    MODULES = [
        start.StartModule,
    ]

    @classmethod
    def register(cls, app):
        for module in cls.MODULES:
            module.setup(app)
