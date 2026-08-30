from app.storage.database import get_connection
from app.stories.text import headline_similarity


def main() -> None:
    with get_connection() as connection:
        articles = connection.execute(
            """
            SELECT id, source_name, title, url
            FROM articles
            ORDER BY id
            """
        ).fetchall()

    matches = []

    for index, first in enumerate(articles):
        for second in articles[index + 1:]:

            # Never compare articles from the same source.
            if first["source_name"] == second["source_name"]:
                continue

            # Ignore exact duplicate headlines.
            if first["title"].strip().lower() == second["title"].strip().lower():
                continue

            score = headline_similarity(
                first["title"],
                second["title"],
            )

            if score > 0:
                matches.append(
                    (
                        score,
                        first,
                        second,
                    )
                )

    matches.sort(key=lambda item: item[0], reverse=True)

    print()
    print("Personal News Feed — Strongest Cross-Source Headline Matches")
    print("=" * 80)
    print()

    print(f"Articles analyzed: {len(articles)}")
    print(
        f"Comparisons made:  {len(articles) * (len(articles) - 1) // 2}"
    )
    print(f"Matching pairs:    {len(matches)}")
    print()

    print("TOP 30 MATCHES")
    print("-" * 80)

    for number, (score, first, second) in enumerate(matches[:30], start=1):
        print()
        print(f"{number}. Similarity: {score:.3f}")
        print(f"   [{first['source_name']}] {first['title']}")
        print(f"   [{second['source_name']}] {second['title']}")


if __name__ == "__main__":
    main()
