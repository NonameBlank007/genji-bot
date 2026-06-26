#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: flood protector
#

import logging
import time
from collections import defaultdict, deque
from functools import wraps

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
)

from ..cfg import SUDO_USER
from ..util.module import Module

logger = logging.getLogger(__name__)
bans = {}


class FloodModule(Module):
    @classmethod
    def setup(cls, app: Application):
        pass


def flood(
    max_messages=3,
    time_window=30,
    ban_duration=300,
    timeout=3,
    flood_message="Blocked for 5 min due to too many requests.",
):
    hits = defaultdict(deque)
    last_use = {}

    def flood_func(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user

            if not user:
                return await func(update, context, *args, **kwargs)

            user_id = user.id

            if user_id == int(SUDO_USER):
                return await func(update, context, *args, **kwargs)

            now = time.time()
            until = bans.get(user_id)

            if until:
                if now < until:
                    remaining = int(until - now)

                    await update.effective_message.reply_text(f"You are blocked from using spammable commands.\nTry again in {remaining}s.")
                    return

                del bans[user_id]

            if timeout:
                last = last_use.get(user_id)

                if last and now - last < timeout:
                    remaining = int(timeout - (now - last))
                    await update.effective_message.reply_text(f"Please wait {remaining}s before using this command again.")
                    return

            h = hits[user_id]
            h.append(now)

            while h and now - h[0] > time_window:
                h.popleft()

            if len(h) > max_messages:
                bans[user_id] = now + ban_duration

                logger.info(f"({user.id}): {update.effective_sender.full_name}: {update.effective_chat.title} ({update.message.chat_id})")
                await update.effective_message.reply_text(flood_message)
                return

            last_use[user_id] = now
            return await func(update, context, *args, **kwargs)

        return wrapper

    return flood_func
