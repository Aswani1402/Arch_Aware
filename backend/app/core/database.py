import logging
import os
import sqlite3
from typing import Optional, Tuple
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings, _DEFAULT_DB_PATH, _BACKEND_DIR, _ROOT_DIR

logger = logging.getLogger("architect_ai.database")


def _validate_sqlite_file(db_path: str) -> Tuple[bool, str]:
    """
    Validate that an existing SQLite file is readable, non-empty, passes quick_check,
    and contains at least one schema table (so a partially copied/truncated file
    cannot be mistaken for a valid production database).
    """
    if not os.path.exists(db_path):
        return False, "file does not exist"
    try:
        if os.path.getsize(db_path) < 100:
            return False, "file size too small to be a valid SQLite database"
        with open(db_path, "rb") as fh:
            header = fh.read(16)
        if header != b"SQLite format 3\x00":
            return False, "invalid SQLite header"
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            cur = conn.cursor()
            qc = cur.execute("PRAGMA quick_check(1)").fetchone()
            if not qc or qc[0] != "ok":
                return False, f"PRAGMA quick_check failed: {qc}"
            table_count = cur.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0]
            if table_count < 1:
                return False, "database contains zero application tables"
        finally:
            conn.close()
        return True, "ok"
    except Exception as exc:
        return False, f"SQLite validation error: {exc}"


def _atomic_copy_sqlite(source_path: str, target_path: str) -> None:
    """
    Atomically copy a validated SQLite seed database into target_path using a
    temporary file + SQLite online backup + quick_check + os.replace().
    Never leaves a partial target file on failure and never overwrites an existing target.
    """
    src_valid, src_reason = _validate_sqlite_file(source_path)
    if not src_valid:
        raise RuntimeError(f"Seed SQLite database at {source_path} is invalid: {src_reason}")

    tmp_path = f"{target_path}.seed.tmp.{os.getpid()}"
    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        src_conn = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
        try:
            dst_conn = sqlite3.connect(tmp_path)
            try:
                src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
        finally:
            src_conn.close()

        tmp_valid, tmp_reason = _validate_sqlite_file(tmp_path)
        if not tmp_valid:
            raise RuntimeError(f"Copied SQLite staging file failed validation: {tmp_reason}")

        os.replace(tmp_path, target_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise


def _is_default_db_path(db_path: str) -> bool:
    """
    Check whether a database file path resolves to the local bundled seed database.
    Case-insensitive and absolute-path aware for Windows/Linux consistency.
    """
    try:
        return os.path.abspath(db_path).lower() == os.path.abspath(_DEFAULT_DB_PATH).lower()
    except Exception:
        return False


def _is_seed_catalogue_path(db_path: str) -> bool:
    """
    Check whether a database file path resolves to the production seed database.
    Ensures that seed artifacts are strictly protected from in-place WAL initialization.
    """
    try:
        norm = os.path.abspath(db_path).lower()
        seed_norm = os.path.abspath(os.path.join(_BACKEND_DIR, "seed_catalogue.sqlite")).lower()
        return norm == seed_norm or os.path.basename(norm).lower() == "seed_catalogue.sqlite"
    except Exception:
        return False


def _is_protected_source_db(db_path: str) -> bool:
    """
    Returns True if db_path resolves to either the original development database
    or the production sanitized seed catalog database.
    """
    return _is_default_db_path(db_path) or _is_seed_catalogue_path(db_path)


def _resolve_seed_path(seed_candidate: Optional[str] = None) -> str:
    """
    Deterministically resolves the seed database path across different working directories
    (e.g., repository root, backend/ directory, or custom paths).
    """
    if seed_candidate:
        candidates = [
            seed_candidate,
            os.path.join(_BACKEND_DIR, seed_candidate),
            os.path.join(_BACKEND_DIR, os.path.basename(seed_candidate)),
            os.path.join(_ROOT_DIR, seed_candidate),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.normpath(os.path.abspath(c))
        return os.path.normpath(os.path.abspath(seed_candidate))

    if os.path.exists(_DEFAULT_DB_PATH):
        return os.path.normpath(os.path.abspath(_DEFAULT_DB_PATH))

    sanitized = os.path.join(_BACKEND_DIR, "seed_catalogue.sqlite")
    if os.path.exists(sanitized):
        return os.path.normpath(os.path.abspath(sanitized))

    return os.path.normpath(os.path.abspath(_DEFAULT_DB_PATH))


def _init_sqlite_wal(db_path: str) -> bool:
    """
    Safely and idempotently set PRAGMA journal_mode=WAL on an external persistent
    SQLite database file (e.g. Render persistent disk mount).
    Strictly guarded to NEVER enable WAL on the local bundled database (_DEFAULT_DB_PATH)
    or the production seed database (seed_catalogue.sqlite).
    """
    if not db_path or db_path == ":memory:":
        return False
    if _is_protected_source_db(db_path):
        logger.debug("[DB] Preserving DELETE journal mode for protected source/seed database: %s", db_path)
        return False

    norm_path = os.path.normpath(db_path)
    if not os.path.exists(norm_path):
        return False

    try:
        conn = sqlite3.connect(norm_path, timeout=5.0)
        try:
            cur = conn.cursor()
            mode = cur.execute("PRAGMA journal_mode;").fetchone()
            current_mode = mode[0].lower() if mode and mode[0] else ""
            if current_mode != "wal":
                cur.execute("PRAGMA journal_mode=WAL;")
                new_mode = cur.execute("PRAGMA journal_mode;").fetchone()
                logger.info(
                    "[DB] Initialized SQLite WAL mode on %s (previous=%s, current=%s)",
                    norm_path,
                    current_mode,
                    new_mode[0] if new_mode else "wal",
                )
            return True
        finally:
            conn.close()
    except Exception as exc:
        logger.warning("[DB] Failed to initialize SQLite WAL mode on %s: %s", norm_path, exc)
        return False


def _ensure_sqlite_persistent_target(
    sqlite_url: str,
    *,
    seed_path: Optional[str] = None,
    allow_empty_production: Optional[bool] = None,
    is_production: Optional[bool] = None,
) -> None:
    """
    For external persistent SQLite mount paths (e.g., Render /var/data/architect_ai.db):
    - Never overwrite an existing database file.
    - Validate any existing external database file so partial copies fail loudly.
    - If target is missing and a valid seed DB exists, copy atomically & validate.
    - In production mode (DEMO_MODE=False), refuse to silently initialize an empty
      database when both the persistent target and seed DB are missing unless
      ALLOW_EMPTY_PRODUCTION_DB=true is explicitly set.
    - Safely enable WAL on external persistent targets, while strictly preserving DELETE
      mode on local bundled/seed databases.
    """
    if not sqlite_url.startswith("sqlite:///") or sqlite_url.startswith("sqlite:///:memory:"):
        return
    target_path = sqlite_url[len("sqlite:///"):]
    if not target_path:
        return
    parent_dir = os.path.dirname(target_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    default_norm = _resolve_seed_path(seed_path or os.environ.get("SQLITE_SEED_DB_PATH"))
    target_norm = os.path.normpath(target_path)

    if os.path.exists(target_norm):
        if not _is_protected_source_db(target_norm):
            ok, reason = _validate_sqlite_file(target_norm)
            if not ok:
                raise RuntimeError(
                    f"Existing persistent SQLite file at {target_norm} is invalid or partially copied ({reason}). "
                    "Refusing to overwrite or start with a corrupted database."
                )
            _init_sqlite_wal(target_norm)
        return

    if target_norm != default_norm and not _is_protected_source_db(target_norm):
        if os.path.exists(default_norm):
            _atomic_copy_sqlite(default_norm, target_norm)
            logger.info("[DB] Atomically seeded persistent SQLite DB at %s", target_norm)
            _init_sqlite_wal(target_norm)
            return

        allow_empty = (
            allow_empty_production
            if allow_empty_production is not None
            else os.environ.get("ALLOW_EMPTY_PRODUCTION_DB", "").strip().lower() == "true"
        )
        is_prod = is_production if is_production is not None else not settings.DEMO_MODE
        if is_prod and not allow_empty:
            raise RuntimeError(
                f"Persistent production SQLite database at {target_norm} does not exist and no seed database "
                f"was found at {default_norm}. Refusing to silently create an empty production database. "
                "Upload/seed architect_ai.db or seed_catalogue.sqlite to the persistent disk or set ALLOW_EMPTY_PRODUCTION_DB=true."
            )


# SQLite needs check_same_thread=False
connect_args = {}
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///."):
    db_url = f"sqlite:///{_DEFAULT_DB_PATH}"

if db_url.startswith("sqlite"):
    _ensure_sqlite_persistent_target(db_url)
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

def configure_sqlite_connection_pragmas(dbapi_connection, connection_record=None):
    """
    Configure runtime SQLite connection pragmas for concurrency hardening.
    Sets busy_timeout=5000ms so concurrent transactions wait rather than
    immediately throwing SQLITE_BUSY / database is locked.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA busy_timeout=5000;")
        finally:
            cursor.close()

if db_url.startswith("sqlite"):
    event.listen(engine, "connect", configure_sqlite_connection_pragmas)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
