from collections import Counter

from app.storage.database import get_connection


def main() -> None:
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT source_name, COUNT(*) AS count
            FROM articles
            GROUP BY source_name
            ORDER BY count DESC
            """
        ).fetchall()

        recent = connection.execute(
            """
            SELECT source_name, title, url
            FROM articles
            ORDER BY id DESC
            LIMIT 25
            """
        ).fetchall()

    print()
    print("Personal News Feed — Database Report")
    print("=" * 70)

    print()
    print(f"Total stored articles: {total}")

    print()
    print("ARTICLES BY SOURCE")
    print("-" * 70)

    for row in rows:
        print(f"{row['source_name']:<30} {row['count']:>5}")

    print()
    print("RECENTLY STORED ARTICLES")
    print("-" * 70)

    for index, row in enumerate(recent, start=1):
        print()
        print(f"{index}. [{row['source_name']}]")
        print(f"   {row['title']}")
        print(f"   {row['url']}")

    print()


if __name__ == "__main__":
    main()
