from config.sources import SOURCES

from app.ingestion.rss import fetch_feed
from app.storage.articles import save_article
from app.storage.database import initialize_database


def main() -> None:
    initialize_database()

    total_fetched = 0
    total_new = 0

    print()
    print("Personal News Feed — RSS Ingestion")
    print("=" * 60)

    for source in SOURCES:
        try:
            items = fetch_feed(source.url, source.name)

            new_count = 0

            for item in items:
                if save_article(item):
                    new_count += 1

            total_fetched += len(items)
            total_new += new_count

            print(
                f"{source.name:<30} "
                f"fetched={len(items):>4} "
                f"new={new_count:>4}"
            )

        except Exception as exc:
            print(
                f"{source.name:<30} "
                f"ERROR: {exc}"
            )

    print("-" * 60)
    print(f"Total fetched: {total_fetched}")
    print(f"Total new:     {total_new}")
    print()


if __name__ == "__main__":
    main()
