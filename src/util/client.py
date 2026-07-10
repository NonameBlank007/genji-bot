#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

import httpx
from telegram.ext import Application

from ..util.logging import logger

client = httpx.AsyncClient(
    http2=True,
    headers={
        "User-Agent": ("GenjiTGBot (https://github.com/nonameblank007/genji-bot)"),
    },
    timeout=10,
    follow_redirects=True,
)


async def shutdown(_app: Application) -> None:
    if client:
        await client.aclose()
        logger.info("External HTTPX closed")
