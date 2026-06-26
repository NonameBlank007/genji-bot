#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: return http dog img
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


@Help.register("dog", "send a http dog image", "Image")
class DogpxModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("dog", get_dogpx))


@flood()
async def get_dogpx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /dog")
        reply = update.message.reply_to_message
        user_text = " ".join(context.args) if context.args else None
        if user_text is not None:
            dogpx_api = f"https://http.dog/{user_text}.jpg"
        else:
            dogpx_api = f"https://http.dog/404.jpg"
        if update.message is not None and not reply:
            await update.message.reply_photo(dogpx_api)
        else:
            await reply.reply_photo(dogpx_api)
    except Exception:
        logger.critical("Could not fetch httpdog api.")
        await update.message.reply_text("Sorry, I couldn't fetch a dog right now. Please try again later")
