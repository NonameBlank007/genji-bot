#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: check bot status
#

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


class StartModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("start", start))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /start")
    await update.message.reply_text("Hello! I'm a bot made by @Noname_Blank")
