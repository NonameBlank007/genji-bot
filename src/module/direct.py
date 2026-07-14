#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends a extracted url
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

from ..util.client import client
from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


@Help.register("rl", "extract a redirected url", "Misc")
class DirectModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("rl", direct))


async def direct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /rl")
    try:
        _support = ("http://", "https://")
        url = " ".join(context.args).strip() if context.args else None
        if url is None:
            await update.message.reply_text("Usage: /rl <link>")
        else:
            if url.startswith(_support):
                logger.info(f"({update.message.from_user.id}): Extraction of URL started")
                msg = await update.message.reply_text("Extracting URL...")
                response = await client.head(url)
                if response.is_success:
                    logger.info(f"({update.message.from_user.id}): Extraction of {url} is success")
                    await msg.edit_text(f"{response.url}")
                else:
                    logger.warning(f"({update.message.from_user.id}): Extraction of {url} failed")
                    await msg.edit_text("Sorry, I couldn't extract URL right now. Please try again later")
            else:
                logger.warning(f"({update.message.from_user.id}): {url} is not valid")
                await update.message.reply_text("URL is not valid.")
    except Exception as e:
        logger.error(f"Error recorded for direct: {e}")
        await update.message.reply_text("Error occurred, I couldn't extract URL right now. Please try again later")
