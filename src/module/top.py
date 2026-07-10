#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: fetch top players of respective
#

import logging
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from ..util.help import Help
from ..util.logging import logger
from ..util.module import Module
from ..util.rw import load

logger = logging.getLogger(__name__)


@Help.register("tops", "show top sexy of chat", "Fun")
@Help.register("topg", "show top gay of chat", "Fun")
class TopModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("tops", tops_command))
        app.add_handler(CallbackQueryHandler(tops_callback, pattern=r"^tops:"))
        app.add_handler(CommandHandler("topg", topg_command))
        app.add_handler(CallbackQueryHandler(topg_callback, pattern=r"^topg:"))


SEXY_DATA_FILE = "sexy_data.json"
GEI_DATA_FILE = "gei_data.json"
PAGE_SIZE = 20


async def tops_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /tops")
    await display_global_ranking(update, context, page=0, is_sexy=True)


async def tops_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[1])
    await display_global_ranking(update, context, page=page, edit_message=True, is_sexy=True)


async def topg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /topg")
    await display_global_ranking(update, context, page=0, is_sexy=False)


async def topg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[1])
    await display_global_ranking(update, context, page=page, edit_message=True, is_sexy=False)


async def display_global_ranking(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, edit_message: bool = False, is_sexy: bool = True
):
    buttons = []
    ranking_lines = []
    row = []

    attribute = "sexy" if is_sexy else "gay"
    attribute_title = "Chat Top Sexy Percentage:" if is_sexy else "Chat Top Gay Percentage:"
    callback = "tops:" if is_sexy else "topg:"
    data_file = SEXY_DATA_FILE if is_sexy else GEI_DATA_FILE
    not_msg = "<i>[°=°] means the user hasn't determined his % today.</i>"

    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    now = datetime.now()
    user_data = load(data_file)
    user_id = str(update.effective_user.id)
    user_exist = user_data.get(user_id)

    sorted_users = [(user_id, data) for user_id, data in user_data.items() if chat_id_str in get_chat_ids(data)]
    sorted_users.sort(key=lambda item: item[1].get("percentage", 0), reverse=True)

    if not sorted_users and (user_exist is None or chat_id_str not in get_chat_ids(user_exist)):
        if update.effective_chat.type == "private":
            await context.bot.send_message(chat_id=chat_id, text="Use in a group")
        else:
            if is_sexy:
                await update.message.reply_text("Calculate sexyness again")
            else:
                await update.message.reply_text("Calculate gayness again")
        return

    total_pages = max((len(sorted_users) - 1) // PAGE_SIZE + 1, 1)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_users = sorted_users[start:end]
    today_str = now.strftime("%Y-%m-%d")

    for rank, (user_id, data) in enumerate(page_users, start=start + 1):
        name = data.get("name", user_id)
        indicator = "[°=°]" if data.get("last_checked") != today_str else ""
        ranking_lines.append(f"<b>{rank}|{name}: <i>{data.get('percentage', 0)}%</i> {attribute} {indicator}</b>")

    ranking_message = "\n".join(ranking_lines)

    if page > 0:
        row.append(InlineKeyboardButton("Back", callback_data=f"{callback}{page - 1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton("Next", callback_data=f"{callback}{page + 1}"))
    if row:
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            f"<u>{attribute_title}\n</u>\n{ranking_message}\n\n{not_msg}", reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            f"<u>{attribute_title}\n</u>\n{ranking_message}\n\n{not_msg}", reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


def get_chat_ids(entry):
    chat_ids = entry.get("chat_ids", [])
    if isinstance(chat_ids, list):
        return [str(chat_id) for chat_id in chat_ids]
    if chat_ids is None:
        return []
    return [str(chat_ids)]
