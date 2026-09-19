import re
from html import unescape


def descript(title, description):
    title = str(title or "")
    description = str(description or "")

    source_match = re.search(r"\(Source:\s*([^)]+)\)", description, re.IGNORECASE)
    source = source_match.group(1).strip() if source_match else "Unknown"

    description = re.sub(r"\s*\(Source:\s*[^)]+\)", "", description, flags=re.IGNORECASE)
    description = re.sub(r"<br\s*/?>", "\n", description, flags=re.IGNORECASE)
    description = re.sub(r"<[^>]+>", "", description)
    description = unescape(description)
    description = re.sub(r"\s+", " ", description).strip()

    if description:
        limit = 200 if len(title) > 50 else 500
        if len(description) > limit:
            description = description[:limit].rsplit(" ", 1)[0] + "..."

    return description, source
