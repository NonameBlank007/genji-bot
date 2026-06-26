#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: configuration file
#

import os

from .util.logging import logger

try:
    from .api_init import TOKEN
except ImportError:
    if not (TOKEN := os.getenv("BOT_TOKEN")):
        logger.critical("Cannot retrive bot token.")
        raise RuntimeError("Cannot get bot token either from cfg file or environment variable.") from None

try:
    from .api_init import SUDO_USER
except ImportError:
    if not (SUDO_USER := os.getenv("MASTER_USER")):
        logger.critical("Cannot retrive sudo user.")
        raise RuntimeError("Cannot get sudo user either from cfg file or environment variable.") from None
