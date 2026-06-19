#!/usr/bin/env python3
#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary: license addition script
#

import sys
from pathlib import Path

HEADER = """\
#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Summary:
#
"""


def add_header(file: Path):
    _path = file.resolve()

    if not _path.exists():
        print(f"File not found: {_path}")
        sys.exit(1)

    content = _path.read_text(encoding="utf-8")

    _path.write_text(HEADER + "\n" + content, encoding="utf-8")
    print(f"Added license -> {_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python 'header.py' 'file.py'")
        sys.exit(1)

    target_path = Path(sys.argv[1]).resolve()

    add_header(target_path)


if __name__ == "__main__":
    main()
