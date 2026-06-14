from ..module import (
    magisk,
    start,
)


class Handlers:
    MODULES = [
        start.StartModule,
        magisk.MagiskModule,
    ]

    @classmethod
    def register(cls, app):
        for module in cls.MODULES:
            module.setup(app)
