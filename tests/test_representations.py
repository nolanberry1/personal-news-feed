from app.stories.representations import ArticleRepresentation, represent_article


def test_article_representation_stores_basic_article_information():
    article = ArticleRepresentation(
        article_id=1,
        title="NASA launches new space telescope",
        source_name="BBC News",
    )

    assert article.article_id == 1
    assert article.title == "NASA launches new space telescope"
    assert article.source_name == "BBC News"
    assert article.embedding is None
    assert article.entities == []


def test_article_representation_can_store_entities():
    article = ArticleRepresentation(
        article_id=1,
        title="NASA launches new space telescope",
        source_name="BBC News",
        entities=[
            {"type": "organization", "text": "NASA"},
            {"type": "event", "text": "space telescope launch"},
        ],
    )

    assert len(article.entities) == 2
    assert article.entities[0]["text"] == "NASA"
    assert article.entities[1]["type"] == "event"


def test_represent_article_builds_representation_from_database_article():
    article = {
        "id": 42,
        "title": "NASA launches new space telescope",
        "source_name": "BBC News",
    }

    representation = represent_article(article)

    assert representation.article_id == 42
    assert representation.title == "NASA launches new space telescope"
    assert representation.source_name == "BBC News"
