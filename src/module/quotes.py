#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends quotes of zen and anime
#

import logging
import random

import httpx
from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


class QuoteModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("quote", quote))
        app.add_handler(CommandHandler("aniote", aniote))


quote_api = [
    "https://zenquotes.io/api/random",
]
aniote_api = [
    "https://yurippe.vercel.app/api/quotes?random=1",
]


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /quote")
        qapi = random.choice(quote_api)
        async with httpx.AsyncClient() as client:
            response = await client.get(qapi)
            quote_data = response.json()
            quote_text = f"{quote_data[0]['q']} - {quote_data[0]['a']}"
            if update.message is not None:
                await update.message.reply_text(quote_text)
    except Exception:
        logger.critical("Could not fetch quote api.")
        await update.message.reply_text("Sorry, I couldn't fetch a quote right now. Please try again later")


async def aniote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /aniote")
        aapi = random.choice(aniote_api)
        async with httpx.AsyncClient() as client:
            response = await client.get(aapi)
            aniote_data = response.json()
            aniote_text = f"{aniote_data[0]['quote']} - {aniote_data[0]['character']} | Show: {aniote_data[0]['show']}"
            if update.message is not None:
                await update.message.reply_text(aniote_text)
    except Exception:
        logger.critical("Could not fetch aniote api.")
        await update.message.reply_text("Sorry, I couldn't fetch a aniote right now. Please try again later")
