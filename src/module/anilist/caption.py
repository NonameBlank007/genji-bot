def caption(title, native, type, status, count, secondary_count, genres, studios, description, source, score, content_type="ANIME"):
    primary_label = "Chapters" if content_type == "MANGA" else "Episodes"
    secondary_label = "Volumes" if content_type == "MANGA" else "Duration"
    secondary_value = secondary_count if content_type == "MANGA" else f"{secondary_count} Min Per Ep."
    status = {"RELEASING": "Ongoing", "NOT_YET_RELEASED": "Upcoming", "CANCELLED": "Cancelled", "FINISHED": "Finished"}.get(status, status)
    studio = "" if content_type == "MANGA" else f"<b>Studios:</b> {studios}\n"
    return f"""<b>{title}</b> (<code>{native}</code>)

<b>Type:</b> {type}
<b>Status:</b> {status}
<b>{primary_label}:</b> {count}
<b>{secondary_label}:</b> {secondary_value}
<b>Score:</b> {score}
<b>Genres:</b> {genres}
{studio}
<i>{description}</i>

<i>(Source: {source})</i>"""
