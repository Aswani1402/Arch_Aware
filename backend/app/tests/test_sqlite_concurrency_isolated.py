import os
import sqlite3
import tempfile
import pytest
from sqlalchemy import create_engine, event
from app.core.config import _DEFAULT_DB_PATH
from app.core.database import (
    _init_sqlite_wal,
    _is_default_db_path,
    _ensure_sqlite_persistent_target,
    configure_sqlite_connection_pragmas,
)


def test_sqlite_busy_timeout_configured():
    """
    Verify that configure_sqlite_connection_pragmas sets PRAGMA busy_timeout=5000
    on SQLite connections.
    """
    eng = create_engine("sqlite:///:memory:")
    event.listen(eng, "connect", configure_sqlite_connection_pragmas)

    with eng.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA busy_timeout;").fetchone()
        assert result is not None
        assert result[0] == 5000


def test_init_sqlite_wal_on_temporary_file():
    """
    Verify that _init_sqlite_wal safely converts a temporary SQLite file to WAL mode
    and is idempotent on subsequent calls.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = os.path.join(tmpdir, "isolated_test.db")

        # Create an initial SQLite database in DELETE journal mode
        conn = sqlite3.connect(test_db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, name TEXT);")
        cur.execute("INSERT INTO sample (name) VALUES ('test');")
        conn.commit()
        initial_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0].lower()
        conn.close()

        assert initial_mode == "delete"

        # Apply _init_sqlite_wal
        success = _init_sqlite_wal(test_db_path)
        assert success is True

        # Verify new journal mode is WAL
        conn = sqlite3.connect(test_db_path)
        cur = conn.cursor()
        new_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0].lower()
        conn.close()

        assert new_mode == "wal"

        # Subsequent call must be idempotent
        second_call = _init_sqlite_wal(test_db_path)
        assert second_call is True


def test_init_sqlite_wal_strictly_refuses_default_db():
    """
    Verify that _init_sqlite_wal strictly refuses to alter the journal mode
    of the local bundled seed database (_DEFAULT_DB_PATH).
    """
    # Test path detection
    assert _is_default_db_path(_DEFAULT_DB_PATH) is True
    assert _is_default_db_path("backend/architect_ai.db") is True
    assert _is_default_db_path(os.path.abspath(_DEFAULT_DB_PATH)) is True

    # Attempt to call _init_sqlite_wal on _DEFAULT_DB_PATH
    result = _init_sqlite_wal(_DEFAULT_DB_PATH)
    assert result is False, "_init_sqlite_wal must return False for _DEFAULT_DB_PATH"

    # Verify journal mode of bundled database remains delete
    conn = sqlite3.connect(f"file:{_DEFAULT_DB_PATH}?mode=ro", uri=True)
    mode = conn.cursor().execute("PRAGMA journal_mode;").fetchone()[0].lower()
    conn.close()

    assert mode == "delete", "Local bundled database journal mode must remain delete"


def test_ensure_sqlite_persistent_target_initializes_wal_for_external_mount():
    """
    Verify that _ensure_sqlite_persistent_target validates, seeds, and applies WAL
    to an external persistent disk target path (e.g. Render /var/data mount simulation).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        seed_db = os.path.join(tmpdir, "seed.db")
        target_db = os.path.join(tmpdir, "target.db")

        # Create seed database
        conn = sqlite3.connect(seed_db)
        cur = conn.cursor()
        cur.execute("CREATE TABLE materials (id INTEGER PRIMARY KEY, name TEXT);")
        cur.execute("INSERT INTO materials (name) VALUES ('Teak');")
        conn.commit()
        conn.close()

        target_url = f"sqlite:///{target_db}"

        # Run _ensure_sqlite_persistent_target
        _ensure_sqlite_persistent_target(target_url, seed_path=seed_db)

        # Target should now exist and be in WAL mode
        assert os.path.exists(target_db)
        conn = sqlite3.connect(target_db)
        cur = conn.cursor()
        mode = cur.execute("PRAGMA journal_mode;").fetchone()[0].lower()
        rows = cur.execute("SELECT name FROM materials;").fetchall()
        conn.close()

        assert mode == "wal"
        assert len(rows) == 1
        assert rows[0][0] == "Teak"

