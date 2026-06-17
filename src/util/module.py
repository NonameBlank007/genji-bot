#!/usr/bin/env python3
#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

from telegram.ext import Application


class Module:
    @classmethod
    def setup(cls, app: Application):
        raise NotImplementedError
