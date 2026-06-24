#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

CMDS = []


class Help:
    @classmethod
    def register(cls, name: str, description: str, type: str):
        def warapper(_class):
            CMDS.append(
                {
                    "name": name,
                    "description": description,
                    "type": type,
                    "module": _class,
                }
            )
            return _class

        return warapper


def get_help():
    return CMDS
