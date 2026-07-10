#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends a nom..nom gif
#

import logging

from telegram import (
    Update,
    constants,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.fetch import fetch
from ..util.flood import flood
from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


@Help.register("nom", "nom..nom..., what you looking at?", "Anime")
class NomModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("nom", nom))


NEKOS_API = "https://nekos.best/api/v2/nom"


EXTRACTORS = {
    NEKOS_API: lambda d: (d["results"][0]["anime_name"], d["results"][0]["url"]),
}


@flood()
async def nom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        anime_name, gif = await fetch(EXTRACTORS)
        reply_to = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /nom")
        await update.message.reply_animation(
            gif,
            caption=f"<b>🎬 Anime</b> • <code>{anime_name}</code>",
            parse_mode=constants.ParseMode.HTML,
            reply_to_message_id=reply_to,
        )
    except Exception:
        logger.critical("Failed to fetch nom")
        await update.message.reply_text("Sorry, I couldn't fetch a nom GIF right now. Please try again later")
