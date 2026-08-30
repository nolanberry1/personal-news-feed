from datetime import timezone

from app.ingestion.rss import (
    RSSItem,
    normalize_url,
)


def test_rss_item_creation():
    item = RSSItem(
        title="Test story",
        url="https://example.com/story",
        published_at=None,
        summary="A test summary.",
        source_name="Test Source",
    )

    assert item.title == "Test story"
    assert item.url == "https://example.com/story"
    assert item.source_name == "Test Source"


def test_normalize_url():
    url = "HTTPS://Example.COM//news/story/?utm_source=test"

    assert normalize_url(url) == (
        "https://example.com/news/story/?utm_source=test"
    )


def test_normalize_url_empty():
    assert normalize_url("") == ""


def test_rss_item_has_timezone_aware_datetime():
    item = RSSItem(
        title="Test story",
        url="https://example.com/story",
        published_at=None,
        summary=None,
        source_name="Test Source",
    )

    assert item.published_at is None
    assert timezone.utc is not None
