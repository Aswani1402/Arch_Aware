import sys
import os
import time

print("[1] Script started", flush=True)
sys.path.insert(0, os.path.abspath("backend"))

print("[2] Importing FastAPI app...", flush=True)
from app.main import app
print("[3] Imported app", flush=True)

from fastapi.testclient import TestClient
print("[4] Creating TestClient...", flush=True)
client = TestClient(app)
print("[5] Created TestClient", flush=True)

print("[6] Making GET request to /api/feed...", flush=True)
t0 = time.time()
r = client.get("/api/feed", params={"q": "Different types of bricks for a house", "page_size": 20})
dur = time.time() - t0
print(f"[7] Received response in {dur:.2f}s: status={r.status_code}", flush=True)
print(f"[8] Items: {len(r.json().get('items', []))}", flush=True)

