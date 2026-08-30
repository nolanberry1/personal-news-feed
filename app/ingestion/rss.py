from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Optional
from urllib.parse import urlsplit, urlunsplit

import feedparser
import httpx


@dataclass
class RSSItem:
    title: str
    url: str
    published_at: Optional[datetime]
    summary: Optional[str]
    source_name: str
    external_id: Optional[str] = None


def normalize_url(url: str) -> str:
    """Normalize a URL enough for comparison and deduplication."""

    url = url.strip()

    if not url:
        return ""

    parts = urlsplit(url)

    if not parts.scheme or not parts.netloc:
        return url

    path = parts.path.replace("//", "/")

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            parts.query,
            "",
        )
    )


def parse_published_at(entry: Any) -> Optional[datetime]:
    """Extract a publication timestamp from a feed entry."""

    for attribute in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attribute, None)

        if parsed:
            return datetime(
                *parsed[:6],
                tzinfo=timezone.utc,
            )

    for attribute in ("published", "updated"):
        value = entry.get(attribute)

        if not value:
            continue

        try:
            parsed = parsedate_to_datetime(value)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except (TypeError, ValueError, OverflowError):
            continue

    return None


def fetch_feed(feed_url: str, source_name: str) -> list[RSSItem]:
    """Fetch and normalize items from an RSS or Atom feed."""

    response = httpx.get(
        feed_url,
        timeout=20.0,
        follow_redirects=True,
        headers={
            "User-Agent": "PersonalNewsFeed/0.1",
        },
    )
    response.raise_for_status()

    feed = feedparser.parse(response.text)

    items: list[RSSItem] = []
    seen_urls: set[str] = set()

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        url = normalize_url(entry.get("link", ""))
        summary = entry.get("summary")

        if not title or not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        external_id = entry.get("id") or entry.get("guid")

        items.append(
            RSSItem(
                title=title,
                url=url,
                published_at=parse_published_at(entry),
                summary=summary,
                source_name=source_name,
                external_id=external_id,
            )
        )

    return items
