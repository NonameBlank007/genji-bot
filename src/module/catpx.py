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


class CatpxModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("cat", get_catpx))


async def get_catpx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(
            f"User: {update.message.from_user.full_name}, Link: {update.message.from_user.link} used /cat command."
        )
        reply = update.message.reply_to_message
        user_text = " ".join(context.args) if context.args else None
        if user_text is not None:
            catpx_api = f"https://httpcats.com/{user_text}"
        else:
            catpx_api = f"https://httpcats.com/404"
        if update.message is not None and not reply:
            await update.message.reply_photo(catpx_api)
        else:
            await reply.reply_photo(catpx_api)
    except Exception:
        logger.critical("Could not fetch httpcat api.")
        await update.message.reply_text("Sorry, I couldn't fetch a cat right now. Please try again later")
