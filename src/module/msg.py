#!/usr/bin/env python3
#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: send a msg
#

import asyncio
import contextlib
import logging

from telegram import (
    Update,
    constants,
    helpers,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


class MsgModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("msg", send_msg))
        app.add_handler(CommandHandler("dmsg", send_dmsg))


async def send_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = " ".join(context.args)  # type: ignore

    logger.info(
        f"({update.message.from_user.id}) in {update.effective_chat.title} ({update.message.chat_id}) used /msg"
    )

    if not txt.strip():
        await update.effective_message.reply_text("Send a text, e.g., /msg hello")
        return

    reply_to = (
        update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
    )
    esp_txt = helpers.escape_markdown(txt.replace(r"\n", "\n"), version=2)

    await asyncio.gather(
        update.effective_chat.send_message(
            esp_txt,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            reply_to_message_id=reply_to,
        ),
    )


async def send_dmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = " ".join(context.args)  # type: ignore

    logger.info(
        f"({update.message.from_user.id}) in {update.effective_chat.title} ({update.message.chat_id}) used /dmsg"
    )

    if not txt.strip():
        await update.effective_message.reply_text("Send a text silently, e.g., /dmsg hello")
        return

    reply_to = (
        update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
    )
    sesp_txt = helpers.escape_markdown(txt.replace(r"\n", "\n"), version=2)

    async def s_del(message):
        with contextlib.suppress(Exception):
            await update.effective_message.delete()

    await asyncio.gather(
        s_del(update.effective_message),
        update.effective_chat.send_message(
            sesp_txt,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            reply_to_message_id=reply_to,
        ),
    )
