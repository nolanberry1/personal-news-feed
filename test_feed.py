from app.ingestion.rss import fetch_feed

FEED_URL = "https://www.ksl.com/rss/news"
SOURCE_NAME = "KSL"

items = fetch_feed(FEED_URL, SOURCE_NAME)

print(f"Fetched {len(items)} items from {SOURCE_NAME}")
print()

for item in items[:10]:
    print(item.title)
    print(item.url)
    print("---")
