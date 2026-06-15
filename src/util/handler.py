from ..module import (
    magisk,
    quotes,
    start,
)


class Handlers:
    MODULES = [
        start.StartModule,
        magisk.MagiskModule,
        quotes.QuoteModule,
    ]

    @classmethod
    def register(cls, app):
        for module in cls.MODULES:
            module.setup(app)
