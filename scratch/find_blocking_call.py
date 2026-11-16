import sys
import os
import faulthandler
import time

faulthandler.dump_traceback_later(5, exit=False)

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal, get_db
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
print("Sending GET /api/feed...", flush=True)
resp = client.get("/api/feed?page_size=20")
print("Response:", resp.status_code, flush=True)

