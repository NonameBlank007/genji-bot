#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: help command module
#

import logging
from collections import defaultdict

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    constants,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from ..util.help import CMDS
from ..util.logging import logger
from ..util.module import Module

logger = logging.getLogger(__name__)
keyboard = []
TYPE_INFO = {
    "Anime": "Give your members enjoyment of funny gif's from anime series.",
    "Image": "Keep group engaged with various images",
    "Misc": "Miscellaneous commands",
    "TE": "Trivia and Entertainment related commands",
}


class HelpModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CallbackQueryHandler(_callback, pattern=r"^help:"))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text, markup = help_menu()
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /help")
    await update.message.reply_text(text, reply_markup=markup, parse_mode=constants.ParseMode.HTML)


def help_menu():
    types = defaultdict(list)

    for cmd in CMDS:
        types[cmd["type"]].append(cmd)

    buttons = [InlineKeyboardButton(t, callback_data=f"help:{t}") for t in sorted(types)]

    keyboard = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

    text = """<b>Help</b>
            
Hey! This is Genji. A bot made by @Noname_Blank for fun and engagement.

<b>Helpful commands:</b>
- /start: Start me.
- /help: Sends this msg again.

If there are any bugs, report @Blank_Network"""

    return text, InlineKeyboardMarkup(keyboard)


async def _callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    action = data[1]

    if action == "back":
        text, markup = help_menu()

        return await query.edit_message_text(text, reply_markup=markup, parse_mode=constants.ParseMode.HTML)

    cmds = [c for c in CMDS if c["type"] == action]

    text = [f"{action}\n\n{TYPE_INFO.get(action)}\n\n<b>{action} commands:</b>"]
    text.extend(f"\n- /{c['name']}: {c['description']}." for c in cmds)
    text = " ".join(text)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="help:back")]])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=constants.ParseMode.HTML)
