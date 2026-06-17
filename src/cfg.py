#!/usr/bin/env python3
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
