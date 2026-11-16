import sys
import os
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print("Sending request to /api/feed...")
resp = client.get("/api/feed", params={"q": "Different types of bricks for a house", "page_size": 20})
print(f"Status: {resp.status_code}")
print(f"Items count: {len(resp.json().get('items', []))}")

