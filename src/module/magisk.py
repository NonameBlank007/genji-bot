import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import Application, CommandHandler, ContextTypes

from ..util.logging import logger
from ..util.module import Module


class MagiskModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("magisk", magisk))


def get_magisk_info(url):
    try:
        data = requests.get(url, timeout=10).json()
        return data["magisk"]["version"], data["magisk"]["link"]
    except Exception:
        logger.critical("Could not fetch contents of magisk.")
        return None, None


stable_version, stable_link = get_magisk_info(
    "https://raw.githubusercontent.com/topjohnwu/magisk-files/master/stable.json"
)

beta_version, beta_link = get_magisk_info("https://raw.githubusercontent.com/topjohnwu/magisk-files/master/beta.json")

canary_version, canary_link = get_magisk_info(
    "https://raw.githubusercontent.com/topjohnwu/magisk-files/master/canary.json"
)


async def magisk(update: Update, contex: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        f"User: {update.message.from_user.full_name}, Link: {update.message.from_user.link} used /magisk command."
    )
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Stable {stable_version}", url=stable_link)],
            [InlineKeyboardButton(f"Beta {beta_version}", url=beta_link)],
            [InlineKeyboardButton(f"Canary {canary_version}", url=canary_link)],
        ]
    )
    await update.message.reply_text("Magisk", reply_markup=reply_markup)
