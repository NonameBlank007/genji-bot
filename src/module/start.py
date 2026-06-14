from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ..util.logging import logger
from ..util.module import Module


class StartModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("start", start))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        f"User: {update.message.from_user.full_name}, Link: {update.message.from_user.link} used /start command."
    )
    await update.message.reply_text("Hello! I'm a bot made by @Noname_Blank")
