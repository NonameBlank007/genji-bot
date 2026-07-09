#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: random % value for a day
#

import asyncio
import logging
import random
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module
from ..util.rw import load, wrt

logger = logging.getLogger(__name__)


@Help.register("gay", "calculate gayness for a day", "Fun")
class GeiModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("gay", gei_command))


GEI_DATA_FILE = "gei_data.json"


async def gei_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /gay")
    await calc_gei(update, context)


async def calc_gei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current_chat_id = str(chat_id)
    _private = update.effective_chat.type == "private"
    _entry = False
    now = datetime.now()
    user_data = load(GEI_DATA_FILE)

    reply_to = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else None
    user_id = (
        update.effective_message.reply_to_message.from_user.id if update.effective_message.reply_to_message else update.message.from_user.id
    )
    user_name = (
        update.effective_message.reply_to_message.from_user.first_name
        if update.effective_message.reply_to_message
        else update.message.from_user.first_name
    )

    user_data_entry = user_data.get(
        str(user_id), {"name": None, "last_checked": (now - timedelta(days=1)).strftime("%Y-%m-%d"), "percentage": None, "chat_ids": []}
    )
    chat_ids = fetch_chat_ids(user_data_entry.get("chat_ids", []))
    if current_chat_id not in chat_ids:
        chat_ids.append(current_chat_id)
        _entry = True
    chat_ids = fetch_chat_ids(chat_ids)
    user_data_entry["chat_ids"] = chat_ids
    user_data_entry["name"] = user_name

    last_checked_date = datetime.strptime(user_data_entry["last_checked"], "%Y-%m-%d")
    ntd = now.date() != last_checked_date.date()

    percentage = user_data_entry["percentage"]
    if percentage is None or ntd:
        _entry = True
        percentage = random.randint(0, 100)
        user_data_entry["last_checked"] = now.strftime("%Y-%m-%d")
        user_data_entry["percentage"] = percentage
    if _entry and not _private:
        await wrt(user_data_entry, user_id, user_data, GEI_DATA_FILE)
    if ntd:
        calc = await update.message.reply_text(f"Calculating gayness...", reply_to_message_id=reply_to)
        await asyncio.sleep(0.3)
        await calc.edit_text(f"{user_name} is {percentage}% gay for today.")
    else:
        await update.message.reply_text(f"{user_name} is {percentage}% gay for today.", reply_to_message_id=reply_to)


def fetch_chat_ids(chat_ids):
    return list(dict.fromkeys(str(id_exist) for id_exist in chat_ids))
