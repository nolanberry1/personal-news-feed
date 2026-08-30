from dataclasses import dataclass, field

import numpy as np

from app.stories.text import get_embedding_model


SIMILARITY_THRESHOLD = 0.60


@dataclass
class StoryCluster:
    articles: list = field(default_factory=list)
    embeddings: list = field(default_factory=list)

    @property
    def sources(self) -> set[str]:
        return {article["source_name"] for article in self.articles}

    @property
    def headline(self) -> str:
        return max(
            self.articles,
            key=lambda article: len(article["title"]),
        )["title"]

    @property
    def centroid(self) -> np.ndarray:
        embeddings = np.vstack(self.embeddings)
        centroid = embeddings.mean(axis=0)
        norm = np.linalg.norm(centroid)
        if norm == 0:
            return centroid
        return centroid / norm


def cluster_articles(articles: list) -> list[StoryCluster]:
    if not articles:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        [article["title"] for article in articles],
        normalize_embeddings=True,
    )

    embeddings = np.asarray(embeddings)

    clusters: list[StoryCluster] = []

    for index, article in enumerate(articles):
        embedding = embeddings[index]

        best_cluster = None
        best_score = -1.0

        for cluster in clusters:
            # Never put two articles from the same source
            # into the same story cluster.
            if article["source_name"] in cluster.sources:
                continue

            score = float(embedding @ cluster.centroid)

            if score > best_score:
                best_score = score
                best_cluster = cluster

        if (
            best_cluster is not None
            and best_score >= SIMILARITY_THRESHOLD
        ):
            best_cluster.articles.append(article)
            best_cluster.embeddings.append(embedding)
        else:
            clusters.append(
                StoryCluster(
                    articles=[article],
                    embeddings=[embedding],
                )
            )

    # Sort the final result deterministically.
    clusters.sort(
        key=lambda cluster: (
            -len(cluster.articles),
            cluster.headline,
        )
    )

    return clusters
