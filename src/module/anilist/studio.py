#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#


def studio(title_y, media, draw, font, color):
    studio_name = ""
    studio_x = 70
    studio_y = title_y + 10

    studios = media.get("studios") or {}
    studio_edges = studios.get("edges") or []
    studio_nodes = studios.get("nodes") or []

    for edge, node in zip(studio_edges, studio_nodes, strict=False):
        if edge.get("isMain"):
            studio_name = node.get("name") or ""
            break

    if not studio_name and studio_nodes:
        studio_name = studio_nodes[0].get("name") or ""

    text_x = studio_x + 60
    text_y = studio_y

    if studio_name:
        draw.text((text_x, text_y), studio_name, font=font, fill=color)
        bbox = draw.textbbox((text_x, text_y), studio_name, font=font)
        text_top, text_bottom = bbox[1], bbox[3]
        text_center = (text_top + text_bottom) / 2

        strip_width = 40
        strip_height = 2
        strip_y = int(text_center - strip_height / 2)
        draw.rectangle((studio_x, strip_y, studio_x + strip_width, strip_y + strip_height), fill=color)
