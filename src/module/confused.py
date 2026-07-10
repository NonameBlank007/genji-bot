#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends a confused gif
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


@Help.register("confused", "give a confused look", "Anime")
class ConfModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("confused", cd))


NEKOS_API = "https://nekos.best/api/v2/confused"


EXTRACTORS = {
    NEKOS_API: lambda d: (d["results"][0]["anime_name"], d["results"][0]["url"]),
}


@flood()
async def cd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        anime_name, gif = await fetch(EXTRACTORS)
        reply_to = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /confused")
        await update.message.reply_animation(
            gif,
            caption=f"<b>🎬 Anime</b> • <code>{anime_name}</code>",
            parse_mode=constants.ParseMode.HTML,
            reply_to_message_id=reply_to,
        )
    except Exception:
        logger.critical("Failed to fetch confused")
        await update.message.reply_text("Sorry, I couldn't fetch a confused GIF right now. Please try again later")
