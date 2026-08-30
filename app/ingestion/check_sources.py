from dataclasses import dataclass

import httpx
import feedparser

from config.sources import SOURCES


@dataclass
class SourceCheck:
    name: str
    status: str
    item_count: int
    error: str | None = None


def check_source(source) -> SourceCheck:
    try:
        response = httpx.get(
            source.url,
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": "PersonalNewsFeed/0.1",
            },
        )

        response.raise_for_status()

        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            return SourceCheck(
                name=source.name,
                status="FAIL",
                item_count=0,
                error="Feed could not be parsed",
            )

        return SourceCheck(
            name=source.name,
            status="OK",
            item_count=len(feed.entries),
        )

    except Exception as exc:
        return SourceCheck(
            name=source.name,
            status="FAIL",
            item_count=0,
            error=str(exc),
        )


def main() -> None:
    print()
    print("Personal News Feed — RSS Source Check")
    print("=" * 60)
    print(f"{'SOURCE':<30} {'STATUS':<10} {'ITEMS':>6}")
    print("-" * 60)

    for source in SOURCES:
        result = check_source(source)

        print(
            f"{result.name:<30} "
            f"{result.status:<10} "
            f"{result.item_count:>6}"
        )

        if result.error:
            print(f"  Error: {result.error}")

    print()


if __name__ == "__main__":
    main()
