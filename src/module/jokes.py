#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: send random jokes
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


@Help.register("joke", "send a random joke", "TE")
class JokeModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("joke", joke))


CHUCKNORRIS_JOKE_API = "https://api.chucknorris.io/jokes/random"
SV443_JOKE_API = "https://sv443.net/jokeapi/v2/joke/Any"
JOKEAPI_API = "https://v2.jokeapi.dev/joke/Any"
OFFICIAL_JOKES_API = "https://official-joke-api.appspot.com/jokes/random"
DAD_JOKES_API = "https://icanhazdadjoke.com/slack"

EXTRACTORS = {
    CHUCKNORRIS_JOKE_API: lambda d: d["value"],
    SV443_JOKE_API: lambda d: f"{d['setup']} {d['delivery']}" if "delivery" in d else d["joke"],
    JOKEAPI_API: lambda d: f"{d['setup']} {d['delivery']}" if "delivery" in d else d["joke"],
    OFFICIAL_JOKES_API: lambda d: f"{d['setup']} {d['punchline']}",
    DAD_JOKES_API: lambda d: d["attachments"][0]["text"],
}


@flood()
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient() as client:
        try:
            joke_txt = await fetch_joke(client)
            logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /joke")
            await update.message.reply_text(joke_txt)
        except Exception:
            logger.critical("Failed to fetch joke")
            await update.message.reply_text("Sorry, I couldn't fetch a joke right now. Please try again later")


async def fetch_joke(client: httpx.AsyncClient) -> str:
    api = random.choice(list(EXTRACTORS))
    response = await client.get(api, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return EXTRACTORS[api](data)
    return ""
