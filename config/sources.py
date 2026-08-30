from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    category: str
    geography: str
    credibility_tier: str


SOURCES = [
    # Utah
    Source(
        name="KSL",
        url="https://www.ksl.com/rss/news",
        category="general",
        geography="utah",
        credibility_tier="high",
    ),
    Source(
        name="ABC4 Utah",
        url="https://www.abc4.com/feed/",
        category="local",
        geography="utah",
        credibility_tier="high",
    ),

    # National
    Source(
        name="NPR",
        url="https://feeds.npr.org/1001/rss.xml",
        category="general",
        geography="us",
        credibility_tier="high",
    ),
    Source(
        name="NBC News",
        url="https://feeds.nbcnews.com/nbcnews/public/news",
        category="general",
        geography="us",
        credibility_tier="high",
    ),
    Source(
        name="CBS News",
        url="https://www.cbsnews.com/latest/rss/main",
        category="general",
        geography="us",
        credibility_tier="high",
    ),
    Source(
        name="PBS NewsHour",
        url="https://www.pbs.org/newshour/feeds/rss/headlines",
        category="general",
        geography="us",
        credibility_tier="high",
    ),

    # World
    Source(
        name="BBC News",
        url="https://feeds.bbci.co.uk/news/rss.xml",
        category="world",
        geography="international",
        credibility_tier="high",
    ),
    Source(
        name="BBC World",
        url="https://feeds.bbci.co.uk/news/world/rss.xml",
        category="world",
        geography="international",
        credibility_tier="high",
    ),
    Source(
        name="The Guardian World",
        url="https://www.theguardian.com/world/rss",
        category="world",
        geography="international",
        credibility_tier="medium",
    ),
    Source(
        name="Al Jazeera",
        url="https://www.aljazeera.com/xml/rss/all.xml",
        category="world",
        geography="international",
        credibility_tier="medium",
    ),
    Source(
        name="France 24",
        url="https://www.france24.com/en/rss",
        category="world",
        geography="international",
        credibility_tier="high",
    ),
]
