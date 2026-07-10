# Genji-Bot
## About
- Genji-Bot is a telegram bot written in Python using the python-telegram-bot library.

- Installation:
  - Install Python (3.13 or later) and uv or use [mise](https://mise.jdx.dev/) to manage the toolchain.
  - Provide setup TOKEN and Master ID in toml or create a api_init.py file in src.
    ```mise.toml
    [env]
    BOT_TOKEN="1234:AbCd1a3....."
    MASTER_USER="1234....."
    ``` 
## Run Bot:
```
$ git clone https://github.com/nonameblank007/genji-bot.git
$ cd genji-bot
$ mise install (optional)
$ uv sync
$ mise deploy (optional)
$ uv run -m src
```

## Devlopment:
```
$ mise dev (optional)
$ uv run jurigged -v -m src
```

# License
IN SHORT of GPL-V3 ensures any changes to source code MUST stay public.

```
SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 2026 Noname Blank <nonameblank007@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```