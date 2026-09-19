from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import ContextTypes


async def character_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    data = query.data or ""
    if not data.startswith("characters_"):
        return

    _, media_type, media_id = data.split("_")
    characters = context.user_data.get(f"characters_{media_type}_{media_id}", [])

    if not characters:
        await query.answer("Character data not found.", show_alert=True)
        return

    await render_character_page(query, characters, media_type, media_id, 0, 10)


async def render_character_page(query, characters, media_type, media_id, page, per_page):
    if not characters:
        return

    total_pages = max(1, (len(characters) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))

    start = page * per_page
    end = start + per_page
    page_characters = characters[start:end]

    character_text = "<b>Characters in series:</b>\n"
    for character in page_characters:
        if not isinstance(character, dict):
            continue

        name = str(character.get("name") or "Unknown")
        role = str(character.get("role") or "Unknown").title()
        character_text += f"• <b>{name}</b> <i>({role})</i>\n"

    keyboard = []
    navigation = []

    if page > 0:
        navigation.append(InlineKeyboardButton(text="Prev", callback_data=f"charpage_{media_type}_{media_id}_{page - 1}"))

    if page < total_pages - 1:
        navigation.append(InlineKeyboardButton(text="Next", callback_data=f"charpage_{media_type}_{media_id}_{page + 1}"))

    if navigation:
        keyboard.append(navigation)

    keyboard.append([InlineKeyboardButton(text="Back", callback_data=f"back_{media_type}_{media_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_caption(caption=character_text, parse_mode=constants.ParseMode.HTML, reply_markup=reply_markup)


async def character_next_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    parts = (query.data or "").split("_")
    if len(parts) < 3:
        return

    _, media_type, media_id, page = parts[:4]
    media_id = int(media_id)
    page = int(page)

    characters = context.user_data.get(f"characters_{media_type}_{media_id}", [])
    if not characters:
        await query.answer("Character data not found.", show_alert=True)
        return

    await render_character_page(query, characters, media_type, media_id, page, 10)
