#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: sends random riddles
#

import logging

import httpx
import orjson as json
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from ..util.flood import flood
from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module
from ..util.rw import load, wrt

logger = logging.getLogger(__name__)


@Help.register("riddle", "sends intresting riddles", "TE")
class RiddleModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("riddle", riddle))
        app.add_handler(CallbackQueryHandler(riddle_answer, pattern=r"^riddle_answer"))


riddle_api_urls = [
    "https://riddles-api.vercel.app/random",
]
RIDDLE_DATA_FILE = "riddles_data.json"


@flood()
async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /riddle")

    user_id = update.effective_user.id

    for url in riddle_api_urls:
        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.critical("Failed to fetch riddle from %s: %s", url, e)
            break

        data = json.loads(response.content)
        question = data["riddle"]
        answer = data["answer"]

        await wrt(None, user_id, None, RIDDLE_DATA_FILE, question, answer)

        message = await update.message.reply_text(
            question,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Answer ➡️", callback_data="riddle_answer")]]),
        )

        context.user_data["current_riddle"] = {  # type: ignore
            "question": question,
            "answer": answer,
            "message_id": message.message_id,
        }

        return

    await update.message.reply_text("Sorry, I couldn't fetch a riddle right now. Please try again later")


async def riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    recent = load(RIDDLE_DATA_FILE).get(user_id)
    if not recent:
        return

    recent = recent[-1]

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=(f"The recent riddle is:\n{recent['question']}\nAnswer: {recent['answer']}"),
    )

    current = context.user_data.get("current_riddle")
    if not current:
        return

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=current["message_id"],
        text=current["question"],
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Answered! ✔️", callback_data="answered"),
                    InlineKeyboardButton(
                        "PM 📬",
                        url=f"https://t.me/{context.bot.username}",
                    ),
                ]
            ]
        ),
    )
