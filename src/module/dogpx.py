import logging

from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


class DogpxModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("dog", get_dogpx))


async def get_dogpx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(
            f"User: {update.message.from_user.full_name}, Link: {update.message.from_user.link} used /dog command."
        )
        user_text = " ".join(context.args) if context.args else None
        if user_text is not None:
            dogpx_api = f"https://http.dog/{user_text}.jpg"
        else:
            dogpx_api = f"https://http.dog/404.jpg"
        if update.message is not None:
            await update.message.reply_photo(dogpx_api)
    except Exception:
        logger.critical("Could not fetch httpdog api.")
        await update.message.reply_text("Sorry, I couldn't fetch a dog right now. Please try again later")
