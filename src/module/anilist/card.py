#
# Copyright (C) 2026 NonameBlank007
#
# SPDX-License-Identifier: GPL-3.0-only
#

import re

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .studio import studio


def pill(card, text, x, y, font, scale=4):
    text = str(text or "")
    bbox = font.getbbox(text)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[0]

    padding_x = 18
    padding_y = 9
    width = text_w + padding_x * 2
    height = text_h + padding_y * 2
    radius = height // 2

    sw = width * scale
    sh = height * scale
    high = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    hd = ImageDraw.Draw(high)

    hd.rounded_rectangle(
        (0, 0, sw - 1, sh - 1),
        radius=radius * scale,
        fill=(255, 255, 255, 38),
        outline=(255, 255, 255, 110),
    )

    high = high.resize((width, height), Image.Resampling.LANCZOS)

    background = card.crop((x, y, x + width, y + height)).convert("RGBA")
    background = background.filter(ImageFilter.GaussianBlur(10))
    background = ImageEnhance.Brightness(background).enhance(1.12)

    mask = Image.new("L", (width, height), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)

    card.paste(background, (x, y), mask)
    card.alpha_composite(high, (x, y))

    draw = ImageDraw.Draw(card)
    draw.text((x + padding_x, y + padding_y - 2), text, font=font, fill=(250, 250, 250, 235))

    return width


def _hex_to_rgb(hex_color):
    if hex_color is None:
        return (255, 255, 255)

    hex_color = str(hex_color).lstrip("#")
    if len(hex_color) != 6:
        return (255, 255, 255)

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _load_fonts():
    return {
        "meta": ImageFont.truetype("fonts/mplus/MPLUSRounded1c-Regular.ttf", 24),
        "title": ImageFont.truetype("fonts/mplus/MPLUSRounded1c-ExtraBold.ttf", 52),
        "studio": ImageFont.truetype("fonts/mplus/MPLUSRounded1c-Bold.ttf", 30),
        "score": ImageFont.truetype("fonts/mplus/MPLUSRounded1c-ExtraBold.ttf", 55),
        "logo": ImageFont.truetype("fonts/isoveka/IosevkaAileNerdFont-Bold.ttf", 45),
        "genre": ImageFont.truetype("fonts/mplus/MPLUSRounded1c-Medium.ttf", 22),
    }


def flow_cut(title, font, max_width=600, max_lines=3, draw=None) -> list[str]:
    title = re.sub(r"\s+", " ", str(title or "")).strip()
    if not title:
        return []
    words = title.split()

    def get_width(text):
        if draw:
            return draw.textbbox((0, 0), text, font)[2]
        return font.getbbox(text)[2]

    lines = []
    words_list = []
    idx = 0

    while idx < len(words) and len(lines) < max_lines:
        candidate_words = words_list + [words[idx]]
        candidate_line = " ".join(candidate_words)
        if get_width(candidate_line) <= max_width:
            words_list.append(words[idx])
            idx += 1
        else:
            if words_list:
                lines.append(words_list)
                words_list = []
            else:
                lines.append([words[idx]])
                idx += 1

    if words_list and len(lines) < max_lines:
        lines.append(words_list)
        words_list = []

    has_overflow = idx < len(words) or bool(words_list)

    res_lines = []
    for i, line_words in enumerate(lines):
        if i == max_lines - 1 and has_overflow:
            while line_words and get_width(" ".join(line_words) + "...") > max_width:
                line_words.pop()
            if line_words:
                res_lines.append(" ".join(line_words) + "...")
            else:
                res_lines.append("...")
        else:
            res_lines.append(" ".join(line_words))

    return res_lines


def card(banner, cover, cv_clr, media, score, title, card_name=None):
    WIDTH = 1200
    HEIGHT = 630
    COVER_W = 500
    COVER_H = 680
    SCALE = 4

    bg = banner.copy()
    scale = max(WIDTH / bg.width, HEIGHT / bg.height)
    bg = bg.resize((int(bg.width * scale), int(bg.height * scale)), Image.Resampling.LANCZOS)

    x = (bg.width - WIDTH) // 2
    y = (bg.height - HEIGHT) // 2
    bg = bg.crop((x, y, x + WIDTH, y + HEIGHT))

    bg = bg.filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)

    card = bg.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (10, 30, 43, 120))
    card = Image.alpha_composite(card, overlay)

    cover_img = cover.copy()
    scale = max(COVER_W / cover_img.width, COVER_H / cover_img.height)
    cover_img = cover_img.resize((int(cover_img.width * scale), int(cover_img.height * scale)), Image.Resampling.LANCZOS)

    cx = (cover_img.width - COVER_W) // 2
    cy = (cover_img.height - COVER_H) // 2
    cover_img = cover_img.crop((cx, cy, cx + COVER_W, cy + COVER_H)).convert("RGBA")

    mask_big = Image.new("L", (COVER_W * SCALE, COVER_H * SCALE), 0)
    mask_draw = ImageDraw.Draw(mask_big)
    mask_draw.polygon(
        [
            (40 * SCALE, 0),
            (COVER_W * SCALE, 0),
            (COVER_W * SCALE, COVER_H * SCALE),
            (0, COVER_H * SCALE),
        ],
        fill=255,
    )
    mask = mask_big.resize((COVER_W, COVER_H), Image.Resampling.LANCZOS)
    cover_img.putalpha(mask)

    card.alpha_composite(cover_img, (700, -20))

    border = Image.new("RGBA", (COVER_W * SCALE, COVER_H * SCALE), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_rgb = _hex_to_rgb(cv_clr)

    glow = Image.new("RGBA", (COVER_W * SCALE, COVER_H * SCALE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line([(40 * SCALE, 0), (0, COVER_H * SCALE)], fill=(*border_rgb, 90), width=8 * SCALE)
    glow = glow.filter(ImageFilter.GaussianBlur(5 * SCALE)).resize((COVER_W, COVER_H), Image.Resampling.LANCZOS)
    card.alpha_composite(glow, (700, -20))

    border_draw.line([(40 * SCALE, 0), (0, COVER_H * SCALE)], fill=(*border_rgb, 190), width=2 * SCALE)
    border = border.resize((COVER_W, COVER_H), Image.Resampling.LANCZOS)
    card.alpha_composite(border, (700, -20))

    draw = ImageDraw.Draw(card)
    fonts = _load_fonts()

    WHITE = (245, 247, 248, 255)
    MUTED = (200, 207, 211, 255)

    season_names = {"WINTER": "Winter", "SPRING": "Spring", "SUMMER": "Summer", "FALL": "Fall"}
    season = media.get("season")
    meta_parts = []

    if season and media.get("seasonYear"):
        meta_parts.append(f"{season_names.get(season, season)} {media['seasonYear']}")
    if media.get("format"):
        meta_parts.append(media["format"])
    if media.get("type") == "MANGA":
        status = media.get("status")

        labels = {
            "RELEASING": "Ongoing",
            "NOT_YET_RELEASED": "Upcoming",
            "CANCELLED": "Cancelled",
            "FINISHED": "Finished",
        }

        if status == "FINISHED" and media.get("chapters"):
            meta_parts.append(f"{media['chapters']} Chapters")

        meta_parts.append(labels.get(status, "Unknown"))

    elif media.get("episodes"):
        meta_parts.append(f"{media['episodes']} Episodes")

    if meta_parts:
        draw.text((60, 55), "  •  ".join(meta_parts), font=fonts["meta"], fill=MUTED)

    title_y = 110
    for line in flow_cut(title, fonts["title"], max_width=600, max_lines=3, draw=draw):
        draw.text((60, title_y), line, font=fonts["title"], fill=WHITE)
        title_y += 70

    studio(title_y, media, draw, fonts["studio"], cv_clr)

    draw.text((70, 443), "", font=fonts["logo"], fill=cv_clr)
    draw.text((137, 434), str(score), font=fonts["score"], fill=MUTED)

    x = 55
    y = 535
    for genre in (media.get("genres") or [])[:4]:
        pill_width = pill(card, genre, x, y, fonts["genre"])
        x += pill_width + 12
        if x > 680:
            break

    card_path = card_name or f"ani_{media.get('id', 'unknown')}.jpg"
    card.convert("RGB").save(card_path, "JPEG", quality=95)
    return card_path
