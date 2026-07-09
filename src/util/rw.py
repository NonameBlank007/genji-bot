#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

import asyncio
import os

import aiofiles
import orjson

_lock = {
    "gei_data.json": asyncio.Lock(),
    "riddles_data.json": asyncio.Lock(),
    "sexy_data.json": asyncio.Lock(),
}


def load(file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            return orjson.loads(f.read())
    else:
        return {}


async def wrt(user_data_entry, user_id, user_data, data_file, question=None, answer=None):
    if user_data_entry is None:
        user_riddles = load(data_file)
        user_riddles[str(user_id)] = [{"question": question, "answer": answer}]
        data = orjson.dumps(user_riddles, option=orjson.OPT_INDENT_2)
    else:
        user_data[str(user_id)] = user_data_entry
        data = orjson.dumps(user_data, option=orjson.OPT_INDENT_2)

    async with _lock[data_file]:
        async with aiofiles.open(data_file, "wb") as f:
            await f.write(data)
