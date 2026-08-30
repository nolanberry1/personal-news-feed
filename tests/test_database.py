from app.storage.database import get_connection, initialize_database


def test_initialize_database(tmp_path, monkeypatch):
    import app.storage.database as database

    test_db = tmp_path / "test.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    initialize_database()

    with get_connection() as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'articles'
            """
        ).fetchall()

    assert len(tables) == 1
