#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends user and chatid
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

from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


@Help.register("did", "retrive chat and user ids", "Misc")
class DIDModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("did", did))


async def did(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        reply = update.message.reply_to_message
        reply_id = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
        text = "Requested IDs:"
        text += f"\nUID: <code>{update.effective_user.id}</code>\nChatID: <code>{update.effective_chat.id}</code>"
        if reply:
            text += f"\n{reply.from_user.first_name}'s UID: <code>{reply.from_user.id}</code>"
        await update.message.reply_text(
            text,
            reply_to_message_id=reply_id,
            parse_mode=constants.ParseMode.HTML,
        )
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /did")
    except Exception as e:
        logger.error(f"caught {e} in did")
        await update.message.reply_text("Sorry, I couldn't fetch id's right now. Please try again later")
