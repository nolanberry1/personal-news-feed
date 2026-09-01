from dataclasses import dataclass, field


@dataclass
class ArticleRepresentation:
    article_id: int
    title: str
    source_name: str
    embedding: object | None = None
    entities: list = field(default_factory=list)


def represent_article(article: dict) -> ArticleRepresentation:
    return ArticleRepresentation(
        article_id=article["id"],
        title=article["title"],
        source_name=article["source_name"],
    )
