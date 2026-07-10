#!/usr/bin/env python3
#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: bot starting point
#

import logging
import time

from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
)
from telegram.request import HTTPXRequest

from .cfg import TOKEN
from .util.client import shutdown
from .util.handler import Handlers
from .util.logging import logger

logger = logging.getLogger(__name__)
request = HTTPXRequest(http_version="2")

logger.info("Starting bot timer")
_start_time = time.time()

app = ApplicationBuilder().token(TOKEN).request(request).rate_limiter(AIORateLimiter()).post_shutdown(shutdown).build()

logger.info("Registering handlers...")
Handlers.register(app)

logger.info("Starting Genji...")
logger.info("Genji Running.")
logger.info(f"Genji took {(time.time() - _start_time):.2f}s to startup.")
app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
