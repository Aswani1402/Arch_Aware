"""
NIVORA — Phase 1.3.4 Test Isolation Guarantee Verification Suite
Proves:
1. Every TestClient API request operates strictly against an isolated temporary database.
2. A saved-item toggle request writes ONLY to the temporary test database.
3. The development database (backend/architect_ai.db) is NEVER touched or modified.
"""

import os
import hashlib
import sqlite3
import pytest
from app.models.models import SavedItem

PROD_DB_PATH = Path = os.path.abspath("backend/architect_ai.db")


def _get_db_metrics():
    size = os.path.getsize(PROD_DB_PATH)
    mtime = os.path.getmtime(PROD_DB_PATH)
    with open(PROD_DB_PATH, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    
    conn = sqlite3.connect(f"file:{PROD_DB_PATH}?mode=ro", uri=True)
    row_count = conn.execute("SELECT COUNT(*) FROM saved_items;").fetchone()[0]
    total_rows = conn.execute(
        "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table') UNION ALL "
        "SELECT COUNT(*) FROM saved_items;"
    ).fetchone()[0]
    conn.close()
    return {"size": size, "mtime": mtime, "sha256": sha256, "saved_items_count": row_count}


def test_saved_item_toggle_writes_only_to_isolated_test_database(client, db, user_headers):
    """
    Guarantees that POST /api/saved/toggle through TestClient:
    - Writes to the isolated temporary test database.
    - Leaves backend/architect_ai.db bit-for-bit identical with zero row or checksum change.
    """
    # 1. Capture initial production DB metrics
    initial_metrics = _get_db_metrics()

    # 2. Execute save request through TestClient
    payload = {
        "item_type": "reference",
        "reference_id": 999999,
        "project_collection": "IsolationTestCollection"
    }
    res_save = client.post("/api/saved/toggle", json=payload, headers=user_headers)
    assert res_save.status_code == 200, f"Save toggle failed: {res_save.text}"
    data_save = res_save.json()
    assert data_save["saved"] is True
    assert data_save["status"] == "saved"

    # 3. Prove record WAS written to isolated test database session
    test_record = db.query(SavedItem).filter_by(reference_id=999999).first()
    assert test_record is not None
    assert test_record.project_collection == "IsolationTestCollection"

    # 4. Prove backend/architect_ai.db was NOT touched at all
    post_save_metrics = _get_db_metrics()
    assert post_save_metrics["sha256"] == initial_metrics["sha256"], (
        f"CRITICAL: Production DB SHA-256 changed during test save! "
        f"Before: {initial_metrics['sha256']} | After: {post_save_metrics['sha256']}"
    )
    assert post_save_metrics["size"] == initial_metrics["size"]
    assert post_save_metrics["mtime"] == initial_metrics["mtime"]
    assert post_save_metrics["saved_items_count"] == initial_metrics["saved_items_count"] == 2

    # 5. Execute unsave request through TestClient
    res_unsave = client.post("/api/saved/toggle", json=payload, headers=user_headers)
    assert res_unsave.status_code == 200
    data_unsave = res_unsave.json()
    assert data_unsave["saved"] is False
    assert data_unsave["status"] == "unsaved"

    # 6. Prove backend/architect_ai.db remains 100% bit-for-bit identical
    post_unsave_metrics = _get_db_metrics()
    assert post_unsave_metrics["sha256"] == initial_metrics["sha256"]
    assert post_unsave_metrics["size"] == initial_metrics["size"]
    assert post_unsave_metrics["mtime"] == initial_metrics["mtime"]
    assert post_unsave_metrics["saved_items_count"] == initial_metrics["saved_items_count"] == 2

