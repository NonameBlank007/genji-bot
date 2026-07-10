#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

import random

import orjson

from ..util.client import client


async def fetch(EXTRACTORS):
    api = random.choice(list(EXTRACTORS))
    response = await client.get(api, timeout=10)
    if response.status_code == 200:
        data = orjson.loads(response.content)
        return EXTRACTORS[api](data)
    return ""
