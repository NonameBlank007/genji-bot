#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: return http plant img
#

import logging

from telegram import (
    Update,
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


@Help.register("plant", "send a http plant image", "Image")
class PlaModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("plant", get_plapx))


@flood()
async def get_plapx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /plant")
        reply = update.message.reply_to_message
        user_text = " ".join(context.args) if context.args else None
        if user_text is not None:
            plapx_api = f"https://http.garden/{user_text}.jpg"
        else:
            plapx_api = f"https://http.garden/404.jpg"
        if update.message is not None and not reply:
            await update.message.reply_photo(plapx_api)
        else:
            await reply.reply_photo(plapx_api)
    except Exception:
        logger.critical("Could not fetch http plant api.")
        await update.message.reply_text("Sorry, I couldn't fetch a plant right now. Please try again later")
