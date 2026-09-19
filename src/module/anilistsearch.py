import logging
from pathlib import Path
from uuid import uuid4

import httpx
import orjson as json
from telegram import InputMediaPhoto, Update, constants
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from ..util.client import client
from ..util.help import Help
from ..util.module import Module
from .anilist.caption import caption
from .anilist.card import card
from .anilist.characters import character_next_page, character_page
from .anilist.keyboard import keyboard
from .anilist.query import (
    cache_paths,
    get_cached_media,
    get_chain_node_page,
    get_chain_relation,
    get_or_create_search_chain,
    img_data,
    info_data,
    query,
    save_chain_page,
    save_media_cache,
    url,
)

logger = logging.getLogger(__name__)


@Help.register("anime", "Search info about a anime", "AniList")
@Help.register("manga", "Search info about a manga", "AniList")
class ASModule(Module):
    @classmethod
    def setup(cls, app: Application):
        app.add_handler(CommandHandler("anime", anime))
        app.add_handler(CommandHandler("manga", manga))
        app.add_handler(CallbackQueryHandler(character_page, pattern=r"^characters_(?:ANIME|MANGA)_\d+$"))
        app.add_handler(CallbackQueryHandler(character_next_page, pattern=r"^charpage_(?:ANIME|MANGA)_\d+_\d+$"))
        app.add_handler(CallbackQueryHandler(media_character_back, pattern=r"^back_(?:ANIME|MANGA)_\d+$"))
        app.add_handler(CallbackQueryHandler(media_result_navigation, pattern=r"^media_nav:[a-z0-9]+$"))
        app.add_handler(CallbackQueryHandler(media_result_page, pattern=r"^media_page:[a-z0-9]+:(?:prev|next)$"))
        app.add_handler(CallbackQueryHandler(media_result_back, pattern=r"^media_back:[a-z0-9]+$"))


async def fetch_media_page(search, page, media_type="ANIME"):
    while True:
        variables = {
            "isAdult": False,
            "search": search,
            "type": media_type,
            "page": page,
            "perPage": 1,
        }

        res = await client.post(
            url=url,
            json={"query": query, "variables": variables},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        res.raise_for_status()

        data = json.loads(res.content)
        page_data = data.get("data", {}).get("Page") or {}
        media = (page_data.get("media") or [None])[0]
        page_info = page_data.get("pageInfo") or {}

        if media or not page_info.get("hasNextPage"):
            return media, page_info

        page += 1


def create_search_session(context, search, media, page_info, media_type="ANIME"):
    session_id = uuid4().hex[:10]
    session_key = f"anime_session_{session_id}"

    context.user_data[session_key] = {
        "search": search,
        "page": page_info.get("currentPage", 1),
        "page_info": page_info,
        "media_id": media["id"],
        "media_type": media_type,
        "chain_id": None,
        "start_media_id": str(media["id"]),
    }
    context.user_data[f"anime_session_for_{media_type}_{media['id']}"] = session_id

    return session_id


def get_session(context, session_id):
    return context.user_data.get(f"anime_session_{session_id}")


def get_media(context, media_id, media_type="ANIME"):
    return context.user_data.get(f"media_{media_type}_{media_id}")


def characters_from_media(media):
    return [
        {
            "name": name,
            "role": edge.get("role") or "UNKNOWN",
        }
        for edge in (media.get("characters") or {}).get("edges", [])
        if (name := ((edge.get("node") or {}).get("name") or {}).get("full"))
    ]


def has_complete_media(media):
    required_fields = {
        "type",
        "id",
        "title",
        "synonyms",
        "season",
        "seasonYear",
        "format",
        "status",
        "episodes",
        "nextAiringEpisode",
        "characters",
        "duration",
        "genres",
        "source",
        "bannerImage",
        "coverImage",
        "averageScore",
        "studios",
        "siteUrl",
        "externalLinks",
        "trailer",
        "description",
        "tags",
    }

    title_fields = {"romaji", "english", "native"}
    cover_fields = {"extraLarge", "large", "medium", "color"}

    return (
        required_fields.issubset(media)
        and title_fields.issubset(media.get("title") or {})
        and cover_fields.issubset(media.get("coverImage") or {})
    )


async def build_media_view(media, session_id=None, session=None, navigation=False):
    (
        title,
        native,
        media_type,
        characters,
        status,
        episodes,
        duration,
        trailer,
        site_url,
        genres,
        studios,
        description,
        source,
        score,
    ) = await info_data(media)

    text = caption(
        title,
        native,
        media_type,
        status,
        episodes,
        duration,
        genres,
        studios,
        description,
        source,
        score,
        media.get("type", "ANIME"),
    )

    session = session or {}
    page_info = session.get("page_info") or {}
    current_page = session.get("page", 1)

    reply_markup = keyboard(
        media["id"],
        site_url,
        trailer,
        characters,
        media_type=media.get("type", "ANIME"),
        session_id=session_id,
        navigation=navigation,
        has_previous=current_page > 1,
        has_next=not session.get("end_of_results", False),
    )

    return text, reply_markup, score, title


async def regenerate_media(media, media_type="ANIME"):
    media_type = media_type.upper()
    _, _, _, _, _, _, _, _, _, _, _, _, _, score = await info_data(media)
    title = media["title"]["english"] or media["title"]["romaji"] or media["title"]["native"]
    cover, banner, cv_clr = await img_data(media)
    image_dir = cache_paths(media_type)
    card_path = image_dir / f"media_{media['id']}.jpg"
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path = card(
        banner,
        cover,
        cv_clr,
        media,
        score,
        title,
        card_name=str(card_path),
    )
    return card_path


async def prepare_media(context, media, session_id, navigation=False):
    media_id = media["id"]
    session = get_session(context, session_id) or {}
    media_type = session.get("media_type", "ANIME")

    context.user_data[f"media_{media_type}_{media_id}"] = media
    context.user_data[f"characters_{media_type}_{media_id}"] = characters_from_media(media)

    text, reply_markup, score, title = await build_media_view(
        media,
        session_id,
        session,
        navigation,
    )

    image_dir = cache_paths(media_type)

    card_path = media.get("_card_path") or str(image_dir / f"media_{media_id}.jpg")
    card_file = Path(card_path)

    if not card_file.exists():
        cover, banner, cv_clr = await img_data(media)
        card_file.parent.mkdir(parents=True, exist_ok=True)

        card_path = card(
            banner,
            cover,
            cv_clr,
            media,
            score,
            title,
            card_name=str(card_file),
        )

        media = save_media_cache(
            media,
            card_path,
            media_type=media_type,
        )

    elif media.get("_card_path") is None:
        save_media_cache(
            media,
            card_path,
            media_type=media_type,
        )

    return media, card_path, text, reply_markup


async def media_character_back(update, context):
    callback_query = update.callback_query
    _, media_type, media_id = callback_query.data.split("_")
    media_id = int(media_id)

    media = get_media(context, media_id, media_type)
    if not media:
        await callback_query.answer("Anime data expired.")
        return

    session_id = context.user_data.get(f"anime_session_for_{media_type}_{media_id}")

    if session_id is None:
        session_id = create_search_session(
            context,
            media["title"].get("romaji") or str(media_id),
            media,
            {"hasNextPage": True},
            media_type,
        )

    await callback_query.answer()

    session = get_session(context, session_id)
    await display_media(callback_query, media, session_id, session)


async def display_media(query, media, session_id=None, session=None):
    text, reply_markup, _, _ = await build_media_view(
        media,
        session_id,
        session,
    )

    await query.edit_message_caption(
        caption=text,
        parse_mode=constants.ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def media_result_navigation(update, context):
    callback_query = update.callback_query
    session_id = callback_query.data.split(":")[1]

    session = get_session(context, session_id)
    if not session:
        await callback_query.answer("Anime search expired.")
        return

    media = get_media(context, session["media_id"], session.get("media_type", "ANIME"))
    if not media:
        await callback_query.answer("Anime data expired.")
        return

    await callback_query.answer()

    *_, reply_markup = await prepare_media(
        context,
        media,
        session_id,
        navigation=True,
    )

    await callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def media_result_page(update, context):
    callback_query = update.callback_query
    _, session_id, direction = callback_query.data.split(":")

    session = get_session(context, session_id)
    if not session:
        await callback_query.answer("Anime search expired.")
        return

    media_type = session.get("media_type", "ANIME")
    current_media_id = str(session["media_id"])
    chain_id = session.get("chain_id")
    if chain_id is None:
        current_media = get_media(context, session["media_id"], media_type)
        if current_media:
            chain_id = get_or_create_search_chain(session["search"], current_media["id"], session.get("page_info"), media_type)
            save_chain_page(chain_id, current_media["id"], session.get("page", 1), session.get("page_info"), media_type=media_type)
            session["chain_id"] = chain_id

    relation_direction = "NEXT" if direction == "next" else "PREVIOUS"
    target_id = get_chain_relation(chain_id, current_media_id, relation_direction, media_type) if chain_id else None
    if target_id and str(target_id) != current_media_id:
        media = get_cached_media(target_id, media_type=media_type)
        if media:
            target_page = get_chain_node_page(chain_id, target_id, media_type) or session["page"]
            session.update(page=target_page, media_id=media["id"], end_of_results=False)
            context.user_data[f"media_{media_type}_{media['id']}"] = media
            context.user_data[f"anime_session_for_{media_type}_{media['id']}"] = session_id
            await callback_query.answer()
            _, card_path, text, reply_markup = await prepare_media(context, media, session_id, navigation=True)
            with open(card_path, "rb") as photo:
                await callback_query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=text, parse_mode=constants.ParseMode.HTML),
                    reply_markup=reply_markup,
                )
            return

    target_page = session["page"] + (1 if direction == "next" else -1)

    if target_page < 1:
        await callback_query.answer("End of results")
        return

    try:
        media, page_info = await fetch_media_page(
            session["search"],
            target_page,
            media_type,
        )
    except (httpx.HTTPError, json.JSONDecodeError):
        await callback_query.answer("Anilist down")
        return

    while media and str(media["id"]) == current_media_id:
        target_page += 1 if direction == "next" else -1
        if target_page < 1:
            media = None
            break
        try:
            media, page_info = await fetch_media_page(
                session["search"],
                target_page,
                media_type,
            )
        except (httpx.HTTPError, json.JSONDecodeError):
            await callback_query.answer("Anilist down")
            return

    if not media:
        await callback_query.answer("End of results")
        session["end_of_results"] = True
        current_media = get_media(context, session["media_id"], media_type)
        if current_media:
            *_, reply_markup = await prepare_media(
                context,
                current_media,
                session_id,
                navigation=True,
            )
            await callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        return

    session.update(
        page=page_info.get("currentPage", target_page),
        page_info=page_info,
        media_id=media["id"],
        end_of_results=False,
    )

    context.user_data[f"anime_session_for_{media_type}_{media['id']}"] = session_id

    await callback_query.answer()

    _, card_path, text, reply_markup = await prepare_media(
        context,
        media,
        session_id,
        navigation=True,
    )

    save_chain_page(
        chain_id,
        media["id"],
        page_info.get("currentPage", target_page),
        page_info,
        previous_media_id=current_media_id if direction == "next" else None,
        next_media_id=current_media_id if direction == "prev" else None,
        media_type=media_type,
    )

    with open(card_path, "rb") as photo:
        await callback_query.edit_message_media(
            media=InputMediaPhoto(
                media=photo,
                caption=text,
                parse_mode=constants.ParseMode.HTML,
            ),
            reply_markup=reply_markup,
        )


async def media_result_back(update, context):
    callback_query = update.callback_query
    session_id = callback_query.data.split(":")[1]

    session = get_session(context, session_id)
    if not session:
        await callback_query.answer("Anime search expired.")
        return

    media = get_media(context, session["media_id"], session.get("media_type", "ANIME"))
    if not media:
        await callback_query.answer("Anime data expired.")
        return

    await callback_query.answer()

    _, _, text, reply_markup = await prepare_media(
        context,
        media,
        session_id,
    )

    await callback_query.edit_message_caption(
        caption=text,
        parse_mode=constants.ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def _send_not_found(update: Update, media_name: str, api_down: bool = False) -> None:
    caption = f"{media_name.title()} not found :("
    if api_down:
        caption += "\nAnilist down. Try again later"
    with open("images/util/404.jpg", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption)


async def media_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    media_type="ANIME",
    media_name="anime",
) -> None:
    txt = " ".join(context.args) if context.args else None

    logger.info(f"({update.message.from_user.id}): {update.effective_chat.title} ({update.message.chat_id}) used /{media_name}")

    if not txt:
        await update.message.reply_text(f"Usage: /{media_name} <{media_name} title>")
        return

    msg = await update.message.reply_text(f"Searching {media_name}...")
    media = get_cached_media(
        txt,
        media_type=media_type,
    )

    page_info = {
        "currentPage": 1,
        "lastPage": 1,
        "hasNextPage": True,
    }

    if media is None or not has_complete_media(media):
        try:
            media, page_info = await fetch_media_page(
                txt,
                1,
                media_type,
            )
        except httpx.HTTPStatusError as e:
            logger.error("AniList request failed: %s", e)
            await msg.delete()
            if e.response.status_code == 404:
                await _send_not_found(update, media_name)
                return

            if e.response.status_code == 403:
                await _send_not_found(update, media_name, api_down=True)
                return

            return

        except (httpx.HTTPError, json.JSONDecodeError):
            await _send_not_found(update, media_name, api_down=True)
            return

    if not media:
        await msg.delete()
        await _send_not_found(update, media_name)
        return

    session_id = create_search_session(
        context,
        txt,
        media,
        page_info,
        media_type,
    )

    media, card_path, text, reply_markup = await prepare_media(
        context,
        media,
        session_id,
    )

    session = get_session(context, session_id)
    chain_id = get_or_create_search_chain(txt, media["id"], page_info, media_type)
    save_chain_page(
        chain_id,
        media["id"],
        page_info.get("currentPage", 1),
        page_info,
        media_type=media_type,
    )
    if session is not None:
        session["chain_id"] = chain_id
        session["start_media_id"] = str(media["id"])

    with open(card_path, "rb") as photo:
        await msg.delete()
        await update.message.reply_photo(
            photo=photo,
            caption=text,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=reply_markup,
        )


async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await media_search(update, context, "ANIME", "anime")


async def manga(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await media_search(update, context, "MANGA", "manga")
