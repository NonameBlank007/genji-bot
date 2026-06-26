#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: send intresting facts
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

from ..util.flood import flood
from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)


@Help.register("fact", "get a random fact", "TE")
class FactModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("fact", fact))


USELESS_FACT_API = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
CAT_FACT_API = "https://catfact.ninja/fact"
DOG_FACT_API = "https://dogapi.dog/api/v2/facts?number=1"


EXTRACTORS = {
    CAT_FACT_API: lambda d: d["fact"],
    DOG_FACT_API: lambda d: d["data"][0]["attributes"]["body"],
    USELESS_FACT_API: lambda d: d["text"],
}


@flood()
async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient() as client:
        try:
            fact = await get_fact(client)
            logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /fact")
            await update.message.reply_text(fact)
        except Exception:
            logger.critical("Could not fetch a fact")
            await update.message.reply_text("Sorry, I couldn't fetch a fact right now. Please try again later")


async def get_fact(client: httpx.AsyncClient) -> str:
    api = random.choice(list(EXTRACTORS))
    response = await client.get(api, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return EXTRACTORS[api](data)
    return ""
