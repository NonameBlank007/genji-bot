#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends a bite gif
#

import logging
import random

import httpx
from telegram import (
    Update,
    constants,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.flood import flood
from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


@Help.register("bite", "bite someone l(*w*)l", "Anime")
class BiteModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("bite", bt))


NEKOS_API = "https://nekos.best/api/v2/bite"


EXTRACTORS = {
    NEKOS_API: lambda d: (d["results"][0]["anime_name"], d["results"][0]["url"]),
}


@flood()
async def bt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient() as client:
        try:
            anime_name, gif = await fetch_bt(client)
            reply_to = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
            logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /bite")
            await update.message.reply_animation(
                gif,
                caption=f"<b>🎬 Anime</b> • <code>{anime_name}</code>",
                parse_mode=constants.ParseMode.HTML,
                reply_to_message_id=reply_to,
            )
        except Exception:
            logger.critical("Failed to fetch bite")
            await update.message.reply_text("Sorry, I couldn't fetch a bite GIF right now. Please try again later")


async def fetch_bt(client: httpx.AsyncClient):
    api = random.choice(list(EXTRACTORS))
    response = await client.get(api, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return EXTRACTORS[api](data)
    return ""
