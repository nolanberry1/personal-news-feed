import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "off",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def normalize_headline(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_headline(text: str) -> set[str]:
    normalized = normalize_headline(text)

    return {
        word
        for word in normalized.split()
        if word not in STOPWORDS
    }


def headline_similarity(first: str, second: str) -> float:
    """
    Return semantic similarity between two headlines.

    Uses sentence embeddings and cosine similarity.
    Returns a value approximately between 0 and 1.
    """
    model = get_embedding_model()

    embeddings = model.encode(
        [first, second],
        normalize_embeddings=True,
    )

    similarity = float(embeddings[0] @ embeddings[1])

    # Cosine similarity can theoretically be negative.
    # Clustering only needs a 0-1 style score.
    if similarity < 0.1:
        return 0.0

    return max(0.0, min(1.0, similarity))
