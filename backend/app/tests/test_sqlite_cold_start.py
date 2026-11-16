import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
import pytest

from app.core.database import (
    _ensure_sqlite_persistent_target,
    _resolve_seed_path,
    _is_protected_source_db,
    _is_seed_catalogue_path,
    _init_sqlite_wal,
    _validate_sqlite_file,
)
from app.core.config import settings, _DEFAULT_DB_PATH, _BACKEND_DIR

SEED_CATALOGUE_PATH = Path(_BACKEND_DIR) / "seed_catalogue.sqlite"


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp(prefix="nivora_cold_start_test_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def test_seed_catalogue_exists_and_is_valid():
    """Verify that the generated production seed catalogue exists and is valid."""
    assert SEED_CATALOGUE_PATH.exists(), f"Seed file missing at {SEED_CATALOGUE_PATH}"
    ok, reason = _validate_sqlite_file(str(SEED_CATALOGUE_PATH))
    assert ok, f"Seed database failed validation: {reason}"

    # Confirm journal mode is DELETE
    conn = sqlite3.connect(f"file:{SEED_CATALOGUE_PATH.as_posix()}?mode=ro", uri=True)
    mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    conn.close()
    assert mode.lower() == "delete", f"Expected DELETE journal mode on seed, got {mode}"


def test_protected_source_db_detection():
    """Verify that default DB and seed catalogue are recognized as protected."""
    assert _is_protected_source_db(str(_DEFAULT_DB_PATH)) is True
    assert _is_protected_source_db(str(SEED_CATALOGUE_PATH)) is True
    assert _is_seed_catalogue_path("seed_catalogue.sqlite") is True
    assert _is_seed_catalogue_path("backend/seed_catalogue.sqlite") is True
    assert _is_protected_source_db("/var/data/architect_ai.db") is False


def test_deterministic_seed_path_resolution():
    """Verify that seed candidate resolves deterministically regardless of working directory."""
    # 1. Direct filename
    res1 = _resolve_seed_path("seed_catalogue.sqlite")
    assert os.path.isabs(res1)
    assert os.path.exists(res1)

    # 2. Path with backend/ prefix
    res2 = _resolve_seed_path("backend/seed_catalogue.sqlite")
    assert os.path.isabs(res2)
    assert os.path.exists(res2)

    # 3. None provided
    res3 = _resolve_seed_path(None)
    assert os.path.isabs(res3)
    assert os.path.exists(res3)


def test_cold_start_empty_target_with_valid_seed(temp_dir):
    """
    Scenario 1: Cold start with empty persistent disk and valid seed.
    Expect: Target copied atomically, validated, and WAL enabled. Seed left in DELETE mode.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    assert not target_path.exists()

    url = f"sqlite:///{target_path.as_posix()}"
    _ensure_sqlite_persistent_target(url, seed_path=str(SEED_CATALOGUE_PATH))

    assert target_path.exists()
    ok, reason = _validate_sqlite_file(str(target_path))
    assert ok, f"Persistent target validation failed: {reason}"

    # Target should be in WAL mode
    conn = sqlite3.connect(str(target_path))
    target_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    fk_violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    target_tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()

    assert target_mode.lower() == "wal"
    assert len(fk_violations) == 0
    assert len(target_tables) == 8

    # Source seed must remain strictly in DELETE mode
    src_conn = sqlite3.connect(f"file:{SEED_CATALOGUE_PATH.as_posix()}?mode=ro", uri=True)
    src_mode = src_conn.execute("PRAGMA journal_mode;").fetchone()[0]
    src_conn.close()
    assert src_mode.lower() == "delete"


def test_cold_start_empty_target_with_missing_seed_fails(temp_dir):
    """
    Scenario 2: Cold start with empty target and missing seed in production mode.
    Expect: Explicit RuntimeError refusing to create empty database.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    missing_seed = temp_dir / "nonexistent_seed.sqlite"

    url = f"sqlite:///{target_path.as_posix()}"
    with pytest.raises(RuntimeError, match="does not exist and no seed database was found"):
        _ensure_sqlite_persistent_target(
            url,
            seed_path=str(missing_seed),
            allow_empty_production=False,
            is_production=True,
        )

    # Target should NOT have been created
    assert not target_path.exists()


def test_cold_start_existing_persistent_database_preserved(temp_dir):
    """
    Scenario 3: Target already exists with pre-existing user/custom data.
    Expect: Seed is NOT copied; target data is strictly preserved.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize target with custom marker
    conn = sqlite3.connect(str(target_path))
    conn.execute("CREATE TABLE custom_marker (id INTEGER PRIMARY KEY, note TEXT);")
    conn.execute("INSERT INTO custom_marker (id, note) VALUES (1, 'persisted_marker');")
    conn.commit()
    conn.close()

    url = f"sqlite:///{target_path.as_posix()}"
    _ensure_sqlite_persistent_target(url, seed_path=str(SEED_CATALOGUE_PATH))

    # Verify custom table and marker remain intact
    conn = sqlite3.connect(str(target_path))
    row = conn.execute("SELECT note FROM custom_marker WHERE id=1;").fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "persisted_marker"


def test_cold_start_existing_target_with_missing_seed_preserved(temp_dir):
    """
    Scenario 4: Target exists, but seed is missing.
    Expect: Target preserved and initialized with WAL; no error raised.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(target_path))
    conn.execute("CREATE TABLE keep_me (id INTEGER PRIMARY KEY);")
    conn.commit()
    conn.close()

    missing_seed = temp_dir / "missing.sqlite"
    url = f"sqlite:///{target_path.as_posix()}"
    _ensure_sqlite_persistent_target(url, seed_path=str(missing_seed))

    assert target_path.exists()


def test_cold_start_repeated_initialization(temp_dir):
    """
    Scenario 5: Repeated application startup.
    Expect: First run seeds; second run does not reseed or wipe changes.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    url = f"sqlite:///{target_path.as_posix()}"

    # First run
    _ensure_sqlite_persistent_target(url, seed_path=str(SEED_CATALOGUE_PATH))
    assert target_path.exists()

    # User modifies target
    conn = sqlite3.connect(str(target_path))
    conn.execute("CREATE TABLE user_mutation (id INTEGER PRIMARY KEY, item TEXT);")
    conn.execute("INSERT INTO user_mutation VALUES (42, 'saved_design');")
    conn.commit()
    conn.close()

    # Second run (restart)
    _ensure_sqlite_persistent_target(url, seed_path=str(SEED_CATALOGUE_PATH))

    conn = sqlite3.connect(str(target_path))
    val = conn.execute("SELECT item FROM user_mutation WHERE id=42;").fetchone()
    conn.close()

    assert val is not None
    assert val[0] == "saved_design"


def test_cold_start_corrupted_seed_fails_safely(temp_dir):
    """
    Scenario 6: Seed is corrupted.
    Expect: Copy aborted, RuntimeError raised, target file cleaned up.
    """
    target_path = temp_dir / "persistent" / "architect_ai.db"
    corrupt_seed = temp_dir / "corrupted_seed.sqlite"
    with open(corrupt_seed, "wb") as f:
        f.write(b"NOT A SQLITE DATABASE HEADER GIBBERISH" * 50)

    url = f"sqlite:///{target_path.as_posix()}"
    with pytest.raises(RuntimeError, match="invalid"):
        _ensure_sqlite_persistent_target(url, seed_path=str(corrupt_seed))

    assert not target_path.exists()


def test_init_sqlite_wal_refuses_protected_seed():
    """Verify that _init_sqlite_wal explicitly refuses to enable WAL on the seed artifact."""
    res = _init_sqlite_wal(str(SEED_CATALOGUE_PATH))
    assert res is False

    conn = sqlite3.connect(f"file:{SEED_CATALOGUE_PATH.as_posix()}?mode=ro", uri=True)
    mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    conn.close()
    assert mode.lower() == "delete"
