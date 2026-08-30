from app.stories.clusters import cluster_articles


def make_article(source_name: str, title: str, article_id: int):
    return {
        "id": article_id,
        "source_name": source_name,
        "title": title,
        "url": f"https://example.com/{article_id}",
    }


def test_clusters_group_same_story_across_sources():
    articles = [
        make_article(
            "KSL",
            "Iceland rejects EU-accession talks in close-fought referendum",
            1,
        ),
        make_article(
            "France 24",
            "Iceland rejects EU accession talks",
            2,
        ),
        make_article(
            "BBC News",
            "Iceland votes against restarting EU membership talks",
            3,
        ),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 1
    assert len(clusters[0].articles) == 3
    assert clusters[0].sources == {"KSL", "France 24", "BBC News"}


def test_clusters_do_not_merge_unrelated_stories():
    articles = [
        make_article(
            "KSL",
            "Iceland rejects EU-accession talks in close-fought referendum",
            1,
        ),
        make_article(
            "France 24",
            "NASA launches new space telescope",
            2,
        ),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2


def test_same_source_articles_do_not_merge():
    articles = [
        make_article(
            "France 24",
            "Iceland rejects EU accession talks",
            1,
        ),
        make_article(
            "France 24",
            "Iceland rejects restarting EU accession talks",
            2,
        ),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2
