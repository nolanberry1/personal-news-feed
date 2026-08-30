import hashlib
from datetime import datetime, timezone

from app.ingestion.rss import RSSItem
from app.storage.database import get_connection


def make_url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def save_article(item: RSSItem) -> bool:
    """Save an article if we haven't seen its URL before.

    Returns True when a new article is inserted.
    """

    url_hash = make_url_hash(item.url)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO articles (
                source_name,
                external_id,
                title,
                url,
                published_at,
                summary,
                discovered_at,
                url_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.source_name,
                item.external_id,
                item.title,
                item.url,
                item.published_at.isoformat()
                if item.published_at
                else None,
                item.summary,
                datetime.now(timezone.utc).isoformat(),
                url_hash,
            ),
        )

    return cursor.rowcount == 1
