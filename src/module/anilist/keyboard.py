from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard(
    media_id,
    site_url,
    trailer,
    characters,
    media_type="ANIME",
    session_id=None,
    navigation=False,
    has_previous=False,
    has_next=True,
):
    row = []
    column = []
    keyboard = []

    if navigation:
        navigation_row = []
        if has_previous:
            navigation_row.append(InlineKeyboardButton(text="Prev", callback_data=f"media_page:{session_id}:prev"))
        if has_next:
            navigation_row.append(InlineKeyboardButton(text="Next", callback_data=f"media_page:{session_id}:next"))

        rows = [navigation_row] if navigation_row else []
        rows.append([InlineKeyboardButton(text="Back", callback_data=f"media_back:{session_id}")])
        return InlineKeyboardMarkup(rows)

    if site_url:
        row.append(InlineKeyboardButton(text="More Info", url=site_url))

    if trailer.get("site") == "youtube" and trailer.get("id"):
        row.append(InlineKeyboardButton(text="🎬 Trailer", url=f"https://www.youtube.com/watch?v={trailer['id']}"))

    if characters:
        column.append(InlineKeyboardButton(text="List Characters", callback_data=f"characters_{media_type}_{media_id}"))

    if row:
        keyboard.append(row)
    if column:
        keyboard.append(column)

    keyboard.append([InlineKeyboardButton(text="Not what you are looking for?", callback_data=f"media_nav:{session_id}")])

    return InlineKeyboardMarkup(keyboard)
