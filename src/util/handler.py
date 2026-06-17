from ..module import (
    catpx,
    dogpx,
    magisk,
    msg,
    plantpx,
    quotes,
    start,
)


class Handlers:
    MODULES = [
        start.StartModule,
        magisk.MagiskModule,
        msg.MsgModule,
        catpx.CatpxModule,
        quotes.QuoteModule,
        dogpx.DogpxModule,
        plantpx.PlaModule,
    ]

    @classmethod
    def register(cls, app):
        for module in cls.MODULES:
            module.setup(app)
