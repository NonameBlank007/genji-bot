import re
import sqlite3
from contextlib import contextmanager
from html import escape
from io import BytesIO
from pathlib import Path

import orjson
from PIL import Image

from ...util.client import client
from ...util.logging import logger
from ..anilist.description import descript

ROOT_DIR = Path(__file__).resolve().parents[3]
CACHE_ROOT = ROOT_DIR / "cache"
MEDIA_CACHE_ROOT = CACHE_ROOT / "anilist"
MEDIA_CACHE_DB_PATHS = {
    "ANIME": MEDIA_CACHE_ROOT / "anime.db",
    "MANGA": MEDIA_CACHE_ROOT / "manga.db",
}
IMAGES_ROOT = ROOT_DIR / "images"
MEDIA_IMAGE_DIRS = {
    "ANIME": IMAGES_ROOT / "anilist" / "anime",
    "MANGA": IMAGES_ROOT / "anilist" / "manga",
}


url = "https://graphql.anilist.co"
query = """query ($isAdult: Boolean = false, $search: String, $id: Int, $type: MediaType, $page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        pageInfo {
            currentPage
            lastPage
            hasNextPage
        }
        media(isAdult: $isAdult, search: $search, id: $id, type: $type) {
      type
      id
      idMal
      title {
        romaji
        english
        native
      }
      isAdult
      synonyms
      season
      seasonYear
      format
      status
      episodes
    chapters
    volumes
      nextAiringEpisode {
        episode
      }
       characters(sort: [ROLE, RELEVANCE]) {
                edges {
                    role
                    node {
                        name {
                            full
                        }
                    }
                }
            }
      duration
      genres
      source
      bannerImage
      coverImage {
        extraLarge
        large
        medium
        color
      }
      averageScore
      studios {
        edges {
          id
          isMain
        }
        nodes {
          id
          name
        }
      }
      siteUrl
      externalLinks {
        url
        type
      }
      trailer {
        id
        site
      }
      description
      tags {
        name
      }
    }
  }
}
"""


def ensure_cache_paths():
    for path in (CACHE_ROOT, MEDIA_CACHE_ROOT, IMAGES_ROOT, *MEDIA_IMAGE_DIRS.values()):
        path.mkdir(parents=True, exist_ok=True)


def cache_paths(media_type):
    return MEDIA_IMAGE_DIRS.get(media_type.upper(), MEDIA_IMAGE_DIRS["ANIME"])


def _connect(db_path=None, media_type="ANIME"):
    ensure_cache_paths()
    connection = sqlite3.connect(db_path or MEDIA_CACHE_DB_PATHS[media_type.upper()])
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS media (
            media_type TEXT NOT NULL,
            media_id TEXT NOT NULL,
            payload BLOB NOT NULL,
            card_path TEXT NOT NULL,
            schema_version INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (media_type, media_id)
        );
        CREATE TABLE IF NOT EXISTS aliases (
            media_type TEXT NOT NULL,
            alias TEXT NOT NULL,
            media_id TEXT NOT NULL,
            PRIMARY KEY (media_type, alias, media_id),
            FOREIGN KEY (media_type, media_id) REFERENCES media(media_type, media_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS aliases_lookup ON aliases(media_type, alias);
        CREATE TABLE IF NOT EXISTS search_chains (
            chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT NOT NULL,
            search_key TEXT NOT NULL,
            search_text TEXT NOT NULL,
            start_media_id TEXT NOT NULL,
            last_page INTEGER,
            has_next_page INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (media_type, start_media_id) REFERENCES media(media_type, media_id)
        );
        CREATE TABLE IF NOT EXISTS chain_nodes (
            chain_id INTEGER NOT NULL,
            page INTEGER NOT NULL,
            media_id TEXT NOT NULL,
            PRIMARY KEY (chain_id, page),
            UNIQUE (chain_id, media_id),
            FOREIGN KEY (chain_id) REFERENCES search_chains(chain_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS chain_relations (
            chain_id INTEGER NOT NULL,
            from_media_id TEXT NOT NULL,
            direction TEXT NOT NULL CHECK (direction IN ('PREVIOUS', 'NEXT')),
            to_media_id TEXT NOT NULL,
            PRIMARY KEY (chain_id, from_media_id, direction),
            FOREIGN KEY (chain_id) REFERENCES search_chains(chain_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS search_chains_lookup ON search_chains(search_key, created_at DESC);
        """
    )

    return connection


@contextmanager
def _connection(db_path=None, media_type="ANIME"):
    connection = _connect(db_path, media_type)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _normalize_cache_text(value):
    if value is None:
        return ""

    text = str(value).strip().lower()
    text = text.replace("https://anilist.co/anime/", "")
    text = text.replace("http://", "").replace("https://", "")
    text = re.sub(r"[-_/]+", " ", text)
    text = re.sub(r"[^0-9a-zA-Z\u00C0-\uFFFF\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_search_key(search):
    return _normalize_cache_text(search)


def get_or_create_search_chain(search, media_id, page_info=None, media_type="ANIME", db_path=None):
    media_type = media_type.upper()
    search_key = normalize_search_key(search)
    page_info = page_info or {}
    last_page = page_info.get("lastPage")
    has_next_page = page_info.get("hasNextPage", True)

    with _connection(db_path, media_type) as connection:
        row = connection.execute(
            "SELECT chain_id, start_media_id FROM search_chains "
            "WHERE media_type = ? AND search_key = ? ORDER BY created_at DESC, chain_id DESC LIMIT 1",
            (media_type, search_key),
        ).fetchone()
        if row and row[1] == str(media_id):
            chain_id = row[0]
            connection.execute(
                "UPDATE search_chains SET last_page = ?, has_next_page = ? WHERE chain_id = ?",
                (last_page, int(bool(has_next_page)), chain_id),
            )
            return chain_id

        cursor = connection.execute(
            "INSERT INTO search_chains "
            "(media_type, search_key, search_text, start_media_id, last_page, has_next_page) VALUES (?, ?, ?, ?, ?, ?)",
            (media_type, search_key, str(search), str(media_id), last_page, int(bool(has_next_page))),
        )
        return cursor.lastrowid


def save_chain_page(
    chain_id,
    media_id,
    page,
    page_info=None,
    previous_media_id=None,
    next_media_id=None,
    media_type="ANIME",
    db_path=None,
):
    page_info = page_info or {}
    with _connection(db_path, media_type) as connection:
        connection.execute(
            "DELETE FROM chain_nodes WHERE chain_id = ? AND media_id = ? AND page != ?",
            (chain_id, str(media_id), int(page)),
        )
        connection.execute(
            "INSERT INTO chain_nodes (chain_id, page, media_id) VALUES (?, ?, ?) "
            "ON CONFLICT(chain_id, page) DO UPDATE SET media_id = excluded.media_id",
            (chain_id, int(page), str(media_id)),
        )
        connection.execute(
            "UPDATE search_chains SET last_page = ?, has_next_page = ? WHERE chain_id = ?",
            (page_info.get("lastPage"), int(bool(page_info.get("hasNextPage", True))), chain_id),
        )
        relations = []
        if previous_media_id is not None:
            relations.append((chain_id, str(media_id), "PREVIOUS", str(previous_media_id)))
            relations.append((chain_id, str(previous_media_id), "NEXT", str(media_id)))
        if next_media_id is not None:
            relations.append((chain_id, str(media_id), "NEXT", str(next_media_id)))
            relations.append((chain_id, str(next_media_id), "PREVIOUS", str(media_id)))
        connection.executemany(
            "INSERT INTO chain_relations (chain_id, from_media_id, direction, to_media_id) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(chain_id, from_media_id, direction) DO UPDATE SET to_media_id = excluded.to_media_id",
            relations,
        )


def get_chain_relation(chain_id, media_id, direction, media_type="ANIME", db_path=None):
    with _connection(db_path, media_type) as connection:
        row = connection.execute(
            "SELECT relations.to_media_id FROM chain_relations AS relations "
            "JOIN media ON media.media_type = ? AND media.media_id = relations.to_media_id "
            "WHERE relations.chain_id = ? AND relations.from_media_id = ? AND relations.direction = ?",
            (media_type.upper(), chain_id, str(media_id), direction.upper()),
        ).fetchone()
    return row[0] if row else None


def get_chain_node_page(chain_id, media_id, media_type="ANIME", db_path=None):
    with _connection(db_path, media_type) as connection:
        row = connection.execute(
            "SELECT page FROM chain_nodes WHERE chain_id = ? AND media_id = ?",
            (chain_id, str(media_id)),
        ).fetchone()
    return row[0] if row else None


def _media_cache_aliases(media):
    aliases = set()
    media_id = media.get("id")
    if media_id is not None:
        aliases.add(str(media_id))
        aliases.add(_normalize_cache_text(media_id))

    title_data = media.get("title") or {}
    for value in title_data.values():
        if not value:
            continue
        aliases.add(str(value))
        aliases.add(_normalize_cache_text(value))

    for synonym in media.get("synonyms") or []:
        if not synonym:
            continue
        aliases.add(str(synonym))
        aliases.add(_normalize_cache_text(synonym))

    site_url = media.get("siteUrl")
    if site_url:
        aliases.add(str(site_url))
        aliases.add(_normalize_cache_text(site_url))

    mal_id = media.get("idMal")
    if mal_id is not None:
        aliases.add(str(mal_id))
        aliases.add(_normalize_cache_text(mal_id))

    return {alias for alias in aliases if alias}


def save_media_cache(media, card_path, media_type="ANIME", db_path=None):
    media_type = media_type.upper()
    media_id = str(media.get("id"))
    entry = dict(media)
    entry["_card_path"] = str(card_path)
    aliases = sorted(_media_cache_aliases(media))
    normalized_aliases = {_normalize_cache_text(alias) for alias in aliases}
    with _connection(db_path, media_type) as connection:
        connection.execute(
            "INSERT INTO media (media_type, media_id, payload, card_path) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(media_type, media_id) DO UPDATE SET payload=excluded.payload, card_path=excluded.card_path",
            (media_type, media_id, orjson.dumps(entry), str(card_path)),
        )
        connection.execute("DELETE FROM aliases WHERE media_type = ? AND media_id = ?", (media_type, media_id))
        connection.executemany(
            "INSERT INTO aliases (media_type, alias, media_id) VALUES (?, ?, ?)",
            ((media_type, alias, media_id) for alias in normalized_aliases if alias),
        )
    return entry


def _load_media(connection, media_type, media_id):
    row = connection.execute(
        "SELECT payload FROM media WHERE media_type = ? AND media_id = ?",
        (media_type, media_id),
    ).fetchone()
    if not row:
        return None
    try:
        return orjson.loads(row[0])
    except (orjson.JSONDecodeError, ValueError):
        return None


def get_cached_media(query, media_type="ANIME", db_path=None):
    if query is None:
        return None
    media_type = media_type.upper()

    normalized_query = _normalize_cache_text(query)

    if not normalized_query:
        return None

    direct_id = str(query).strip()

    if direct_id.isdigit():
        media_id = str(int(direct_id))

        with _connection(db_path, media_type) as connection:
            return _load_media(connection, media_type, media_id)

    with _connection(db_path, media_type) as connection:
        rows = connection.execute(
            "SELECT media_id FROM aliases WHERE media_type = ? AND alias = ?",
            (media_type, normalized_query),
        ).fetchall()
        if len(rows) != 1:
            return None
        return _load_media(connection, media_type, rows[0][0])


async def info_data(media):
    title = media["title"]["english"] or media["title"]["romaji"] or media["title"]["native"]
    native = media["title"]["native"] or []
    media_format = media.get("format") or "N/A"
    genres = ", ".join(media.get("genres") or []) or "N/A"
    status = media.get("status") or "N/A"
    if media.get("type") == "MANGA":
        ep = media.get("chapters") or "N/A"
        duration = media.get("volumes") or "N/A"
    else:
        ep = media.get("episodes") or "N/A"
        duration = media.get("duration") or "N/A"
    trailer = media.get("trailer") or {}
    site_url = media.get("siteUrl") or None
    studios = ", ".join(studio["name"] for studio in (media.get("studios") or {}).get("nodes", [])) or "N/A"
    description, source = descript(media["title"]["romaji"], media.get("description") or "N/A")
    description = escape(description)
    score = (media.get("averageScore") or 0) / 10
    return (
        title,
        native,
        media_format,
        media.get("characters") or {},
        status,
        ep,
        duration,
        trailer,
        site_url,
        genres,
        studios,
        description,
        source,
        score,
    )


async def img_data(media):
    cover_url = media["coverImage"]["extraLarge"]
    banner_url = media["bannerImage"] or cover_url

    cover_image_response = await client.get(cover_url)
    banner_image_response = await client.get(banner_url)

    cover = Image.open(BytesIO(cover_image_response.content)).convert("RGB")
    banner = Image.open(BytesIO(banner_image_response.content)).convert("RGB")

    cv_clr = media["coverImage"]["color"] or "#A8B6BA"
    return cover, banner, cv_clr
