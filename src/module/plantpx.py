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


class PlaModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("plant", get_plapx))


async def get_plapx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(
            f"User: {update.message.from_user.full_name}, Link: {update.message.from_user.link} used /plant command."
        )
        user_text = " ".join(context.args) if context.args else None
        if user_text is not None:
            plapx_api = f"https://http.garden/{user_text}.jpg"
        else:
            plapx_api = f"https://http.garden/404.jpg"
        if update.message is not None:
            await update.message.reply_photo(plapx_api)
    except Exception:
        logger.critical("Could not fetch http plant api.")
        await update.message.reply_text("Sorry, I couldn't fetch a plant right now. Please try again later")
