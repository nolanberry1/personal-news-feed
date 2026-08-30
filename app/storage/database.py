import sqlite3
from pathlib import Path


DB_PATH = Path("data/news.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                external_id TEXT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                published_at TEXT,
                summary TEXT,
                discovered_at TEXT NOT NULL,
                url_hash TEXT NOT NULL UNIQUE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_articles_published_at
            ON articles(published_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_articles_source
            ON articles(source_name)
            """
        )


def article_exists(url_hash: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM articles
            WHERE url_hash = ?
            LIMIT 1
            """,
            (url_hash,),
        ).fetchone()

    return row is not None
